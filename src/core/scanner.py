"""
HEX-AVG Scanner Module
Main scanning engine with detection capabilities
"""

import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from .file_traversal import FileTraversal
from .hasher import FileHasher
from .multithreading import ThreadManager, ProgressCallback

from config import HEXAVGConfig


class HEXAVGScanner:
    """Main scanner class for HEX-AVG"""
    
    def __init__(
        self,
        threads: int = None,
        enable_heuristics: bool = True,
        enable_yara: bool = False
    ):
        self.threads = threads or HEXAVGConfig.DEFAULT_THREADS
        self.enable_heuristics = enable_heuristics
        self.enable_yara = enable_yara and HEXAVGConfig.IS_LINUX
        
        self.file_traversal = FileTraversal()
        self.file_hasher = FileHasher()
        self.thread_manager = ThreadManager(max_workers=self.threads)
        
        self.scan_stats = {
            'start_time': None,
            'end_time': None,
            'duration': 0,
            'files_scanned': 0,
            'files_skipped': 0,
            'threats_found': 0,
            'threats': []
        }
        
        # Initialize detection modules
        self.signature_detector = None
        self.heuristic_detector = None
        self.yara_detector = None
        try:
            from src.detection.signature import SignatureDetector
            self.signature_detector = SignatureDetector()
        except Exception as e:
            print(f"[!] Signature detector unavailable: {e}")
        if self.enable_heuristics:
            try:
                from src.detection.heuristic import HeuristicDetector
                self.heuristic_detector = HeuristicDetector()
            except Exception as e:
                print(f"[!] Heuristic detector unavailable: {e}")
        if self.enable_yara:
            try:
                from src.detection.yara_engine import YARADetector
                self.yara_detector = YARADetector()
            except Exception as e:
                print(f"[!] YARA unavailable (continuing without it): {e}")
    
    def scan(
        self,
        scan_path: Path,
        quick_scan: bool = False,
        progress_callback: Optional[callable] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        self.scan_stats['start_time'] = time.time()
        
        if not scan_path.exists():
            raise FileNotFoundError(f"Scan path not found: {scan_path}")
        
        skip_extensions = HEXAVGConfig.QUICK_SCAN_SKIP_EXTENSIONS if quick_scan else None
        
        print(f"\n{'='*60}")
        print(f"HEX-AVG Scanner v{HEXAVGConfig.VERSION}")
        print(f"{'='*60}")
        print(f"Scan Path: {scan_path}")
        print(f"Scan Type: {'Quick' if quick_scan else 'Full'}")
        print(f"Threads: {self.threads}")
        print(f"Heuristics: {'Enabled' if self.enable_heuristics else 'Disabled'}")
        print(f"YARA Rules: {'Enabled' if self.enable_yara else 'Disabled'}")
        print(f"Dry Run: {'Yes' if dry_run else 'No'}")
        print(f"{'='*60}\n")
        
        print("Discovering files...")
        file_paths = self.file_traversal.get_files_list(
            scan_path,
            skip_extensions=skip_extensions
        )
        
        traversal_stats = self.file_traversal.get_statistics()
        print(f"Found {traversal_stats['files_scanned']} files to scan\n")
        
        if progress_callback is None:
            progress_callback = ProgressCallback("Scanning files")
        
        print("Starting scan...")
        scan_results = self.thread_manager.scan_files(
            file_paths,
            self._scan_file,
            progress_callback=progress_callback
        )
        
        self._process_scan_results(scan_results)
        
        self.scan_stats['end_time'] = time.time()
        self.scan_stats['duration'] = (
            self.scan_stats['end_time'] - self.scan_stats['start_time']
        )
        
        self._print_scan_summary()
        
        return self.scan_stats
    
    def _scan_file(self, file_path: Path) -> Dict[str, Any]:
        result = {
            'file_path': str(file_path),
            'status': 'clean',
            'threats': [],
            'hashes': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            file_size = file_path.stat().st_size
            if file_size > HEXAVGConfig.MAX_SCAN_FILE_SIZE:
                result['status'] = 'skipped'
                result['reason'] = f'File too large ({file_size} bytes)'
                return result
            
            result['hashes'] = self.file_hasher.hash_file(file_path)
            
            if self.signature_detector:
                signature_result = self.signature_detector.detect(file_path, result['hashes'])
                if signature_result['detected']:
                    result['status'] = 'infected'
                    result['threats'].append({
                        'type': 'signature',
                        'name': signature_result['name'],
                        'severity': signature_result['severity']
                    })
            
            if self.enable_heuristics and self.heuristic_detector:
                heuristic_result = self.heuristic_detector.analyze(file_path, file_size)
                if heuristic_result.get('suspicious'):
                    if result['status'] == 'clean':
                        result['status'] = 'suspicious'
                    result['threats'].extend(heuristic_result.get('threats', []))
            
            if self.enable_yara and self.yara_detector:
                yara_result = self.yara_detector.scan(file_path)
                if yara_result.get('matches'):
                    result['status'] = 'infected'
                    for match in yara_result['matches']:
                        result['threats'].append({
                            'type': 'yara',
                            'name': match.get('rule', 'yara_match'),
                            'severity': 'high'
                        })
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    def _process_scan_results(self, results: List[Dict[str, Any]]) -> None:
        for result in results:
            self.scan_stats['files_scanned'] += 1
            
            if result['status'] in ('skipped', 'error'):
                self.scan_stats['files_skipped'] += 1
            
            if result.get('threats'):
                self.scan_stats['threats_found'] += 1
                self.scan_stats['threats'].append(result)
    
    def _print_scan_summary(self) -> None:
        duration = self.scan_stats['duration']
        
        print(f"\n{'='*60}")
        print("SCAN SUMMARY")
        print(f"{'='*60}")
        print(f"Files Scanned: {self.scan_stats['files_scanned']}")
        print(f"Files Skipped: {self.scan_stats['files_skipped']}")
        print(f"Threats Found: {self.scan_stats['threats_found']}")
        print(f"Scan Duration: {duration:.2f} seconds")
        
        if self.scan_stats['threats_found'] > 0:
            print(f"\n{'='*60}")
            print("THREATS DETECTED:")
            print(f"{'='*60}")
            for threat in self.scan_stats['threats'][:10]:
                print(f"\nFile: {threat['file_path']}")
                for t in threat['threats']:
                    print(f"  - Type: {t.get('type')}, Name: {t.get('name')}, Severity: {t.get('severity')}")
            
            if self.scan_stats['threats_found'] > 10:
                print(f"\n... and {self.scan_stats['threats_found'] - 10} more threats")
        
        print(f"{'='*60}\n")
    
    def quick_scan(self, scan_path: Path) -> Dict[str, Any]:
        return self.scan(scan_path, quick_scan=True)
    
    def full_scan(self, scan_path: Path) -> Dict[str, Any]:
        return self.scan(scan_path, quick_scan=False)
    
    def get_statistics(self) -> Dict[str, Any]:
        return self.scan_stats.copy()
    
    def reset_statistics(self) -> None:
        self.scan_stats = {
            'start_time': None,
            'end_time': None,
            'duration': 0,
            'files_scanned': 0,
            'files_skipped': 0,
            'threats_found': 0,
            'threats': []
        }
        self.file_traversal.reset_statistics()
        self.thread_manager.reset_statistics()
    
    def __del__(self):
        if hasattr(self, 'thread_manager'):
            self.thread_manager.shutdown(wait=False)
