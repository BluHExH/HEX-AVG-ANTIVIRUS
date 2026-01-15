"""
HEX-AVG Heuristic Detection Module
Analyzes files for suspicious patterns and behaviors
"""

import math
from pathlib import Path
from typing import Dict, List, Any

from config import HEXAVGConfig


class HeuristicDetector:
    """Heuristic analysis for detecting suspicious files"""
    
    def __init__(self):
        """Initialize heuristic detector"""
        self.entropy_threshold_high = HEXAVGConfig.ENTROPY_THRESHOLD_HIGH
        self.entropy_threshold_low = HEXAVGConfig.ENTROPY_THRESHOLD_LOW
        self.suspicious_extensions = HEXAVGConfig.get_platform_extensions()
        self.min_executable_size = HEXAVGConfig.MIN_EXECUTABLE_SIZE
        self.max_executable_size = HEXAVGConfig.MAX_EXECUTABLE_SIZE
    
    def analyze(
        self,
        file_path: Path,
        file_size: int = None
    ) -> Dict[str, Any]:
        """
        Perform heuristic analysis on a file
        
        Args:
            file_path: Path to the file
            file_size: Size of the file in bytes (optional)
        
        Returns:
            Analysis result dictionary
        """
        result = {
            'suspicious': False,
            'threats': [],
            'confidence': 0.0
        }
        
        if file_size is None:
            try:
                file_size = file_path.stat().st_size
            except Exception:
                return result
        
        # Check file extension
        ext_threats = self._check_extension(file_path)
        if ext_threats:
            result['suspicious'] = True
            result['threats'].extend(ext_threats)
            result['confidence'] += 0.3
        
        # Check file size anomalies
        size_threats = self._check_size_anomalies(file_path, file_size)
        if size_threats:
            result['suspicious'] = True
            result['threats'].extend(size_threats)
            result['confidence'] += 0.2
        
        # Check double extensions
        double_ext_threats = self._check_double_extensions(file_path)
        if double_ext_threats:
            result['suspicious'] = True
            result['threats'].extend(double_ext_threats)
            result['confidence'] += 0.4
        
        # Calculate entropy for executable files
        if self._is_executable(file_path):
            try:
                entropy = self._calculate_entropy(file_path)
                entropy_threats = self._check_entropy(entropy)
                if entropy_threats:
                    result['suspicious'] = True
                    result['threats'].extend(entropy_threats)
                    result['confidence'] += 0.5
            except Exception:
                pass
        
        # Normalize confidence
        result['confidence'] = min(result['confidence'], 1.0)
        
        return result
    
    def _check_extension(self, file_path: Path) -> List[Dict[str, str]]:
        """Check if file has suspicious extension"""
        threats = []
        ext = file_path.suffix.lower()
        
        if ext in self.suspicious_extensions:
            threats.append({
                'type': 'suspicious_extension',
                'name': f'Suspicious file extension: {ext}',
                'severity': 'medium'
            })
        
        return threats
    
    def _check_size_anomalies(
        self,
        file_path: Path,
        file_size: int
    ) -> List[Dict[str, str]]:
        """Check for abnormal file sizes"""
        threats = []
        ext = file_path.suffix.lower()
        
        # Check if executable
        if ext in self.suspicious_extensions:
            # Check for tiny executables
            if file_size < self.min_executable_size:
                threats.append({
                    'type': 'size_anomaly',
                    'name': f'Unusually small executable: {file_size} bytes',
                    'severity': 'high'
                })
            
            # Check for oversized executables
            elif file_size > self.max_executable_size:
                threats.append({
                    'type': 'size_anomaly',
                    'name': f'Unusually large executable: {file_size} bytes',
                    'severity': 'medium'
                })
        
        return threats
    
    def _check_double_extensions(self, file_path: Path) -> List[Dict[str, str]]:
        """Check for double file extensions"""
        threats = []
        name = file_path.name.lower()
        
        # Check for double extensions (e.g., .pdf.exe)
        parts = name.split('.')
        if len(parts) > 2:
            # Check if last extension is executable
            last_ext = parts[-1]
            if last_ext in [e.lstrip('.') for e in self.suspicious_extensions]:
                threats.append({
                    'type': 'double_extension',
                    'name': f'Double extension detected: {name}',
                    'severity': 'high'
                })
        
        return threats
    
    def _is_executable(self, file_path: Path) -> bool:
        """Check if file is likely an executable"""
        ext = file_path.suffix.lower()
        return ext in self.suspicious_extensions
    
    def _calculate_entropy(self, file_path: Path) -> float:
        """
        Calculate Shannon entropy of a file
        
        Args:
            file_path: Path to the file
        
        Returns:
            Entropy value (0-8)
        """
        try:
            with open(file_path, 'rb') as f:
                data = f.read(4096)  # Read first 4KB for efficiency
            
            if not data:
                return 0.0
            
            # Count byte frequencies
            byte_counts = [0] * 256
            for byte in data:
                byte_counts[byte] += 1
            
            # Calculate entropy
            entropy = 0.0
            data_len = len(data)
            
            for count in byte_counts:
                if count > 0:
                    probability = count / data_len
                    entropy -= probability * math.log2(probability)
            
            return entropy
        
        except Exception:
            return 0.0
    
    def _check_entropy(self, entropy: float) -> List[Dict[str, str]]:
        """Check if entropy indicates suspicious activity"""
        threats = []
        
        if entropy > self.entropy_threshold_high:
            threats.append({
                'type': 'high_entropy',
                'name': f'High entropy detected ({entropy:.2f}): possible packing/encryption',
                'severity': 'high'
            })
        elif entropy < self.entropy_threshold_low:
            threats.append({
                'type': 'low_entropy',
                'name': f'Low entropy detected ({entropy:.2f}): possible simple payload',
                'severity': 'low'
            })
        
        return threats
    
    def scan_directory(
        self,
        directory_path: Path
    ) -> List[Dict[str, Any]]:
        """
        Scan all files in a directory
        
        Args:
            directory_path: Path to directory
        
        Returns:
            List of suspicious files
        """
        suspicious_files = []
        
        if not directory_path.is_dir():
            return suspicious_files
        
        for file_path in directory_path.rglob('*'):
            if file_path.is_file():
                result = self.analyze(file_path)
                if result['suspicious']:
                    result['file_path'] = str(file_path)
                    suspicious_files.append(result)
        
        return suspicious_files