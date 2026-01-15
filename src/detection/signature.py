"""
HEX-AVG Signature-Based Detection Module
Detects malware using hash matching against signature database
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from config import HEXAVGConfig


class SignatureDetector:
    """Signature-based malware detection using hash matching"""
    
    def __init__(self):
        """Initialize signature detector"""
        self.signature_db = HEXAVGConfig.SIGNATURE_DB
        self.connection = None
        
        # Load signatures
        self._initialize_database()
        self._load_eicar_signature()
    
    def _initialize_database(self) -> None:
        """Initialize SQLite signature database"""
        try:
            # Create database directory if it doesn't exist
            self.signature_db.parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to database
            self.connection = sqlite3.connect(str(self.signature_db))
            cursor = self.connection.cursor()
            
            # Create signatures table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signatures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    md5 TEXT,
                    sha1 TEXT,
                    sha256 TEXT,
                    type TEXT,
                    severity TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for faster lookups
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_md5 ON signatures(md5)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sha1 ON signatures(sha1)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sha256 ON signatures(sha256)')
            
            self.connection.commit()
        
        except Exception as e:
            print(f"Error initializing signature database: {str(e)}")
            if self.connection:
                self.connection.close()
            raise
    
    def _load_eicar_signature(self) -> None:
        """Load EICAR test signature from JSON file"""
        eicar_file = HEXAVGConfig.SIGNATURES_DIR / "eicar.json"
        
        if not eicar_file.exists():
            return
        
        try:
            with open(eicar_file, 'r') as f:
                data = json.load(f)
            
            for sig in data.get('signatures', []):
                self.add_signature(
                    name=sig['name'],
                    md5=sig.get('md5'),
                    sha1=sig.get('sha1'),
                    sha256=sig.get('sha256'),
                    sig_type=sig.get('type'),
                    severity=sig.get('severity'),
                    description=sig.get('description')
                )
        
        except Exception as e:
            print(f"Error loading EICAR signature: {str(e)}")
    
    def add_signature(
        self,
        name: str,
        md5: Optional[str] = None,
        sha1: Optional[str] = None,
        sha256: Optional[str] = None,
        sig_type: str = "unknown",
        severity: str = "medium",
        description: str = ""
    ) -> bool:
        """
        Add a signature to the database
        
        Args:
            name: Signature name
            md5: MD5 hash
            sha1: SHA1 hash
            sha256: SHA256 hash
            sig_type: Type of signature
            severity: Severity level
            description: Description
        
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO signatures (name, md5, sha1, sha256, type, severity, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, md5, sha1, sha256, sig_type, severity, description))
            
            self.connection.commit()
            return True
        
        except Exception as e:
            print(f"Error adding signature: {str(e)}")
            return False
    
    def detect(
        self,
        file_path: Path,
        hashes: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Detect malware by matching hashes against signatures
        
        Args:
            file_path: Path to the file
            hashes: Dictionary of hashes (md5, sha1, sha256)
        
        Returns:
            Detection result dictionary
        """
        result = {
            'detected': False,
            'name': None,
            'severity': None,
            'type': None,
            'description': None
        }
        
        try:
            cursor = self.connection.cursor()
            
            # Check each hash algorithm
            for algo, hash_value in hashes.items():
                if not hash_value:
                    continue
                
                # Query database for matching signature
                cursor.execute(f'''
                    SELECT name, severity, type, description
                    FROM signatures
                    WHERE {algo} = ?
                    LIMIT 1
                ''', (hash_value,))
                
                row = cursor.fetchone()
                if row:
                    result['detected'] = True
                    result['name'] = row[0]
                    result['severity'] = row[1]
                    result['type'] = row[2]
                    result['description'] = row[3]
                    result['matched_hash'] = algo
                    break
        
        except Exception as e:
            print(f"Error during detection: {str(e)}")
        
        return result
    
    def get_signature_count(self) -> int:
        """Get total number of signatures"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT COUNT(*) FROM signatures')
            count = cursor.fetchone()[0]
            return count
        except Exception:
            return 0
    
    def list_signatures(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List signatures in the database
        
        Args:
            limit: Maximum number of signatures to return
        
        Returns:
            List of signature dictionaries
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT name, md5, sha256, type, severity, description, created_at
                FROM signatures
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            signatures = []
            for row in cursor.fetchall():
                signatures.append({
                    'name': row[0],
                    'md5': row[1],
                    'sha256': row[2],
                    'type': row[3],
                    'severity': row[4],
                    'description': row[5],
                    'created_at': row[6]
                })
            
            return signatures
        
        except Exception as e:
            print(f"Error listing signatures: {str(e)}")
            return []
    
    def export_signatures(self, output_file: Path) -> bool:
        """
        Export signatures to JSON file
        
        Args:
            output_file: Path to output JSON file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            signatures = self.list_signatures(limit=None)
            
            with open(output_file, 'w') as f:
                json.dump({
                    'signatures': signatures,
                    'count': len(signatures),
                    'exported_at': str(HEXAVGConfig.VERSION)
                }, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error exporting signatures: {str(e)}")
            return False
    
    def import_signatures(self, input_file: Path) -> bool:
        """
        Import signatures from JSON file
        
        Args:
            input_file: Path to input JSON file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(input_file, 'r') as f:
                data = json.load(f)
            
            count = 0
            for sig in data.get('signatures', []):
                if self.add_signature(
                    name=sig['name'],
                    md5=sig.get('md5'),
                    sha1=sig.get('sha1'),
                    sha256=sig.get('sha256'),
                    sig_type=sig.get('type', 'unknown'),
                    severity=sig.get('severity', 'medium'),
                    description=sig.get('description', '')
                ):
                    count += 1
            
            print(f"Imported {count} signatures")
            return True
        
        except Exception as e:
            print(f"Error importing signatures: {str(e)}")
            return False
    
    def clear_signatures(self) -> bool:
        """Clear all signatures from database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM signatures')
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error clearing signatures: {str(e)}")
            return False
    
    def close(self) -> None:
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def __del__(self):
        """Cleanup when detector is destroyed"""
        self.close()