"""
Advanced Heuristic Detection Engine for HEX-AVG
Implements multi-signal heuristic analysis for unknown malware detection
"""

import os
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import struct
import re


class AdvancedHeuristicEngine:
    """
    Advanced heuristic detection engine using multiple signals:
    - File entropy analysis (packed/encrypted content detection)
    - File type vs extension mismatch
    - Suspicious string patterns
    - Packed/obfuscated file indicators
    - Script behavior patterns
    """
    
    def __init__(self):
        # Suspicious strings commonly found in malware
        self.suspicious_strings = [
            # Process injection
            r'VirtualAlloc',
            r'WriteProcessMemory',
            r'CreateRemoteThread',
            r'SetWindowsHookEx',
            
            # Malware URLs/IPs
            r'http://\d+\.\d+\.\d+\.\d+',  # IP-based URLs
            r'ftp://.*@.*',  # FTP with credentials
            
            # Registry manipulation
            r'RegOpenKey',
            r'RegSetValue',
            r'RegDeleteValue',
            
            # Obfuscation
            r'base64',
            r'xor',
            r'rot13',
            r'eval\(',  # Dynamic code execution
            
            # Anti-debugging
            r'IsDebuggerPresent',
            r'CheckRemoteDebuggerPresent',
            r'NtQueryInformationProcess',
            
            # Crypto/Encoding
            r'AES\.encrypt',
            r'Rijndael',
            r'RC4',
            r'DES',
            
            # Network
            r'socket\(',
            r'bind\(',
            r'listen\(',
            r'connect\(',
        ]
        
        self.suspicious_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.suspicious_strings
        ]
        
        # Known packing tools signatures
        self.packing_signatures = {
            b'UPX': 'UPX Packer',
            b'PECompact': 'PECompact',
            b'ASPack': 'ASPack',
            b'NSPack': 'NSPack',
            b'Petite': 'Petite',
            b'MEW': 'MEW',
            b'FSG': 'FSG',
            b'MPRESS': 'MPRESS',
            b'Themida': 'Themida',
            b'VMProtect': 'VMProtect',
        }
        
        # File type signatures (magic bytes)
        self.file_signatures = {
            b'MZ': 'exe',  # PE executable
            b'\x7fELF': 'elf',  # ELF executable
            b'PK\x03\x04': 'zip',  # ZIP archive
            b'PK\x05\x06': 'zip',
            b'PK\x07\x08': 'zip',
            b'\x1f\x8b': 'gz',  # GZIP
            b'BZh': 'bz2',  # BZIP2
            b'Rar!': 'rar',  # RAR
            b'\xfd7zXZ\x00': 'xz',  # XZ
            b'\x89PNG': 'png',  # PNG image
            b'\xff\xd8\xff': 'jpg',  # JPEG image
            b'GIF8': 'gif',  # GIF image
            b'%PDF': 'pdf',  # PDF document
            b'\x25\x21\x50\x53\x2d\x41\x64\x6f\x62\x65': 'ps',  # PostScript
        }
        
        # Suspicious extensions for executables
        self.executable_extensions = {
            '.exe', '.dll', '.sys', '.scr', '.com', '.pif', '.bat', '.cmd', 
            '.vbs', '.js', '.jar', '.msi', '.cpl', '.app', '.elf', '.bin',
            '.sh', '.bash', '.py', '.pl', '.rb', '.php', '.ps1'
        }
        
        # Known benign file types
        self.benign_extensions = {
            '.txt', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.mp3', '.mp4',
            '.avi', '.mkv', '.zip', '.rar', '.7z', '.tar', '.gz', '.log'
        }
    
    def analyze_file(self, file_path: Path) -> Dict:
        """
        Perform comprehensive heuristic analysis on a file
        
        Returns:
            Dict containing:
            - risk_score (0-100): Overall risk score
            - signals: Individual detection signals
            - explanation: Human-readable explanation
        """
        if not file_path.exists():
            return {'risk_score': 0, 'signals': [], 'explanation': 'File not found'}
        
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read(1024 * 1024)  # Read first 1MB for analysis
            
        except (IOError, PermissionError) as e:
            return {
                'risk_score': 0,
                'signals': [],
                'explanation': f'Could not read file: {str(e)}'
            }
        
        # Collect all signals
        signals = []
        total_score = 0
        
        # Signal 1: Entropy Analysis (0-30 points)
        entropy_result = self._analyze_entropy(file_data)
        if entropy_result['score'] > 0:
            signals.append(entropy_result)
            total_score += entropy_result['score']
        
        # Signal 2: File Type vs Extension Mismatch (0-25 points)
        mismatch_result = self._check_extension_mismatch(file_path, file_data)
        if mismatch_result['score'] > 0:
            signals.append(mismatch_result)
            total_score += mismatch_result['score']
        
        # Signal 3: Suspicious Strings (0-25 points)
        strings_result = self._detect_suspicious_strings(file_data)
        if strings_result['score'] > 0:
            signals.append(strings_result)
            total_score += strings_result['score']
        
        # Signal 4: Packed/Obfuscated Files (0-20 points)
        packer_result = self._detect_packer(file_data)
        if packer_result['score'] > 0:
            signals.append(packer_result)
            total_score += packer_result['score']
        
        # Cap score at 100
        total_score = min(total_score, 100)
        
        # Generate explanation
        explanation = self._generate_explanation(signals, total_score)
        
        return {
            'risk_score': total_score,
            'signals': signals,
            'explanation': explanation
        }
    
    def _analyze_entropy(self, data: bytes) -> Dict:
        """
        Analyze file entropy to detect packed/encrypted content
        
        Why this works:
        - High entropy (>7.5) indicates packed/encrypted content
        - Normal files have lower entropy (~4-6)
        - Malware often uses packing to evade detection
        """
        if len(data) < 256:
            return {'score': 0, 'name': 'entropy', 'details': 'File too small for entropy analysis'}
        
        # Calculate byte frequency
        freq = [0] * 256
        for byte in data:
            freq[byte] += 1
        
        # Calculate Shannon entropy
        entropy = 0.0
        data_len = len(data)
        for count in freq:
            if count > 0:
                probability = count / data_len
                entropy -= probability * math.log2(probability)
        
        # Score based on entropy
        if entropy >= 7.5:
            score = 30  # Very high - likely packed or encrypted
            level = 'CRITICAL'
        elif entropy >= 7.0:
            score = 25  # High - suspicious
            level = 'HIGH'
        elif entropy >= 6.5:
            score = 15  # Medium - worth investigating
            level = 'MEDIUM'
        elif entropy >= 5.5:
            score = 5   # Low - normal for some file types
            level = 'LOW'
        else:
            score = 0   # Normal
            level = 'NONE'
        
        return {
            'score': score,
            'name': 'entropy',
            'level': level,
            'details': f'Entropy: {entropy:.2f} (normal: 4.0-6.0, packed: >7.0)'
        }
    
    def _check_extension_mismatch(self, file_path: Path, data: bytes) -> Dict:
        """
        Check if file extension matches actual file type
        
        Why this works:
        - Malware often disguises executables as benign files
        - Examines actual file content vs extension
        - Common disguise: .exe file renamed to .jpg
        """
        extension = file_path.suffix.lower()
        
        # Detect actual file type from magic bytes
        actual_type = None
        for signature, file_type in self.file_signatures.items():
            if data.startswith(signature):
                actual_type = file_type
                break
        
        if not actual_type:
            return {'score': 0, 'name': 'extension_mismatch', 'details': 'Could not determine file type'}
        
        # Check for mismatch
        # Case 1: Executable disguised as benign file
        if actual_type in ['exe', 'elf'] and extension in self.benign_extensions:
            return {
                'score': 25,
                'name': 'extension_mismatch',
                'level': 'CRITICAL',
                'details': f'Executable disguised as {extension} file (malware disguise technique)'
            }
        
        # Case 2: Archive disguised as image
        if actual_type == 'zip' and extension in ['.jpg', '.jpeg', '.png', '.gif']:
            return {
                'score': 20,
                'name': 'extension_mismatch',
                'level': 'HIGH',
                'details': f'Archive disguised as {extension} file (malware delivery technique)'
            }
        
        # Case 3: Script with wrong extension
        if actual_type == 'txt' and extension in self.executable_extensions:
            # This could be legitimate, but worth noting
            return {
                'score': 10,
                'name': 'extension_mismatch',
                'level': 'MEDIUM',
                'details': f'File extension suggests executable but content is text'
            }
        
        return {'score': 0, 'name': 'extension_mismatch', 'details': 'Extension matches file type'}
    
    def _detect_suspicious_strings(self, data: bytes) -> Dict:
        """
        Detect suspicious API calls and patterns
        
        Why this works:
        - Malware uses specific Windows APIs for malicious behavior
        - Process injection, registry manipulation, obfuscation
        - These patterns are rare in legitimate software
        """
        try:
            text_content = data.decode('utf-8', errors='ignore')
        except:
            text_content = str(data)
        
        matches = []
        for pattern in self.suspicious_patterns:
            found = pattern.findall(text_content)
            if found:
                matches.extend(found[:3])  # Limit to 3 matches per pattern
        
        if not matches:
            return {'score': 0, 'name': 'suspicious_strings', 'details': 'No suspicious strings found'}
        
        # Score based on number of matches
        match_count = len(set(matches))
        if match_count >= 10:
            score = 25
            level = 'CRITICAL'
        elif match_count >= 5:
            score = 20
            level = 'HIGH'
        elif match_count >= 3:
            score = 15
            level = 'MEDIUM'
        elif match_count >= 1:
            score = 10
            level = 'LOW'
        else:
            score = 5
            level = 'LOW'
        
        return {
            'score': score,
            'name': 'suspicious_strings',
            'level': level,
            'details': f'Found {match_count} suspicious strings: {", ".join(set(matches)[:5])}'
        }
    
    def _detect_packer(self, data: bytes) -> Dict:
        """
        Detect known packers/obfuscators
        
        Why this works:
        - Malware authors use packers to evade signature detection
        - Packers leave specific signatures in the file
        - Known packers: UPX, Themida, VMProtect, etc.
        """
        packer_name = None
        for signature, name in self.packing_signatures.items():
            if signature in data[:1024]:  # Check first 1KB
                packer_name = name
                break
        
        if packer_name:
            return {
                'score': 20,
                'name': 'packer_detected',
                'level': 'HIGH',
                'details': f'File appears to be packed with {packer_name} (obfuscation technique)'
            }
        
        # Check for generic packing indicators
        # High entropy + small sections = likely packed
        if self._analyze_entropy(data)['score'] >= 20:
            return {
                'score': 15,
                'name': 'packer_detected',
                'level': 'MEDIUM',
                'details': 'High entropy suggests possible custom packing or encryption'
            }
        
        return {'score': 0, 'name': 'packer_detected', 'details': 'No packer detected'}
    
    def _generate_explanation(self, signals: List[Dict], total_score: int) -> str:
        """Generate human-readable explanation of heuristic analysis"""
        
        if total_score == 0:
            return "File appears benign based on heuristic analysis"
        
        explanation_parts = []
        
        # Overall assessment
        if total_score >= 70:
            explanation_parts.append("⚠️  HIGH RISK: File exhibits multiple suspicious characteristics")
        elif total_score >= 40:
            explanation_parts.append("⚡ MEDIUM RISK: File has some suspicious indicators")
        elif total_score >= 20:
            explanation_parts.append("🔔 LOW RISK: File has minor suspicious characteristics")
        else:
            explanation_parts.append("ℹ️  MINIMAL RISK: File has few suspicious indicators")
        
        # Individual signals
        if signals:
            explanation_parts.append("\nDetected signals:")
            for signal in signals:
                if signal['score'] > 0:
                    explanation_parts.append(
                        f"  • [{signal.get('level', 'INFO')}] {signal['name']}: {signal['details']}"
                    )
        
        # Recommendations
        if total_score >= 70:
            explanation_parts.append(
                "\n🛡️  RECOMMENDATION: Quarantine this file immediately and do not execute"
            )
        elif total_score >= 40:
            explanation_parts.append(
                "\n🔍 RECOMMENDATION: Exercise caution - scan with multiple antivirus tools before executing"
            )
        
        return "\n".join(explanation_parts)