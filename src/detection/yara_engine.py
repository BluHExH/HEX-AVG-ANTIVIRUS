"""
HEX-AVG YARA Engine Module
YARA rule-based detection for Linux systems
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

from config import HEXAVGConfig

# Only import yara on Linux
if HEXAVGConfig.IS_LINUX:
    try:
        import yara
        YARA_AVAILABLE = True
    except ImportError:
        YARA_AVAILABLE = False
else:
    YARA_AVAILABLE = False


class YARADetector:
    """YARA rule-based detection engine"""
    
    def __init__(self):
        """Initialize YARA detector"""
        self.rules = {}
        self.rules_dir = HEXAVGConfig.YARA_RULES_DIR
        self.initialized = False
        
        # Only initialize on Linux with yara-python
        if HEXAVGConfig.IS_LINUX and YARA_AVAILABLE:
            self._load_rules()
    
    def _load_rules(self) -> None:
        """Load YARA rules from rules directory"""
        if not YARA_AVAILABLE:
            print("YARA not available - install yara-python")
            return
        
        try:
            # Find all .yar files in rules directory
            rule_files = list(self.rules_dir.glob("*.yar"))
            
            if not rule_files:
                print("No YARA rules found")
                return
            
            # Compile each rule file
            for rule_file in rule_files:
                try:
                    rule_name = rule_file.stem
                    self.rules[rule_name] = yara.compile(str(rule_file))
                    print(f"Loaded YARA rule: {rule_name}")
                except Exception as e:
                    print(f"Error compiling rule {rule_file}: {str(e)}")
            
            self.initialized = bool(self.rules)
        
        except Exception as e:
            print(f"Error loading YARA rules: {str(e)}")
    
    def scan(self, file_path: Path) -> Dict[str, Any]:
        """
        Scan a file using YARA rules
        
        Args:
            file_path: Path to the file
        
        Returns:
            Scan result dictionary
        """
        result = {
            'scanned': False,
            'matches': [],
            'errors': []
        }
        
        if not self.initialized:
            result['errors'].append("YARA engine not initialized")
            return result
        
        if not file_path.exists() or not file_path.is_file():
            result['errors'].append(f"File not found: {file_path}")
            return result
        
        try:
            result['scanned'] = True
            
            # Scan with all loaded rules
            for rule_name, rules in self.rules.items():
                try:
                    matches = rules.match(str(file_path))
                    
                    for match in matches:
                        result['matches'].append({
                            'rule': match.rule,
                            'namespace': match.namespace,
                            'tags': match.tags,
                            'meta': match.meta,
                            'strings': [s for s in match.strings]
                        })
                
                except Exception as e:
                    result['errors'].append(f"Error with rule {rule_name}: {str(e)}")
        
        except Exception as e:
            result['errors'].append(f"Scan error: {str(e)}")
        
        return result
    
    def scan_directory(self, directory_path: Path) -> List[Dict[str, Any]]:
        """
        Scan all files in a directory
        
        Args:
            directory_path: Path to directory
        
        Returns:
            List of scan results with matches
        """
        results = []
        
        if not directory_path.is_dir():
            return results
        
        for file_path in directory_path.rglob('*'):
            if file_path.is_file():
                result = self.scan(file_path)
                if result['matches']:
                    result['file_path'] = str(file_path)
                    results.append(result)
        
        return results
    
    def compile_rule(self, rule_text: str, rule_name: str = "custom") -> bool:
        """
        Compile a custom YARA rule
        
        Args:
            rule_text: YARA rule text
            rule_name: Name for the rule
        
        Returns:
            True if successful, False otherwise
        """
        if not YARA_AVAILABLE:
            print("YARA not available")
            return False
        
        try:
            compiled_rule = yara.compile(source=rule_text)
            self.rules[rule_name] = compiled_rule
            return True
        except Exception as e:
            print(f"Error compiling rule: {str(e)}")
            return False
    
    def add_rule_file(self, rule_file: Path) -> bool:
        """
        Add a YARA rule file
        
        Args:
            rule_file: Path to .yar file
        
        Returns:
            True if successful, False otherwise
        """
        if not YARA_AVAILABLE:
            print("YARA not available")
            return False
        
        try:
            rule_name = rule_file.stem
            self.rules[rule_name] = yara.compile(str(rule_file))
            return True
        except Exception as e:
            print(f"Error adding rule file: {str(e)}")
            return False
    
    def get_rules_count(self) -> int:
        """Get number of loaded rules"""
        return len(self.rules)
    
    def list_rules(self) -> List[str]:
        """List loaded rule names"""
        return list(self.rules.keys())