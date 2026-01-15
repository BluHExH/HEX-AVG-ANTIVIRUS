"""
Cloud Signature Sync (Optional/Opt-In)
Hash-only cloud queries with offline fallback and privacy protection
"""

import hashlib
from pathlib import Path
from typing import Dict, List, Optional
import json


class CloudSyncClient:
    """
    Cloud signature synchronization client
    
    Privacy-First Design:
    - ONLY hashes are sent to the cloud (never file contents)
    - User must explicitly opt-in
    - Offline mode always available
    - Clear privacy explanations
    - No file uploads, no telemetry beyond hash queries
    
    Use Case:
    - Check if file hash is known malicious in cloud database
    - Provides additional detection layer beyond local signatures
    - Reduces false negatives for new threats
    """
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.cache_file = Path(__file__).parent.parent.parent / "cloud_cache.json"
        self.cache = self._load_cache()
        self.offline_mode = False
        
        # In production, this would be your actual cloud API endpoint
        # For now, we simulate cloud responses
        self.api_endpoint = "https://api.hex-avg.org/v1/hash-lookup"
        
        # Privacy notice
        self.privacy_notice = """
╔════════════════════════════════════════════════════════════════╗
║              CLOUD SIGNATURE SYNC - PRIVACY NOTICE            ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  🔒 PRIVACY-FIRST DESIGN:                                      ║
║                                                                ║
║  What is sent to the cloud:                                   ║
║  • File HASHES ONLY (MD5, SHA1, SHA256)                       ║
║  • No file contents                                           ║
║  • No file names                                              ║
║  • No file paths                                              ║
║  • No personal information                                    ║
║  • No telemetry                                                ║
║                                                                ║
║  What is NOT sent to the cloud:                               ║
║  ✗ File contents                                              ║
║  ✗ File names                                                 ║
║  ✗ File paths                                                 ║
║  ✗ Personal data                                              ║
║  ✗ Usage statistics                                           ║
║  ✗ System information                                         ║
║                                                                ║
║  How it works:                                                 ║
║  1. HEX-AVG calculates file hash locally                      ║
║  2. Only the hash is sent to cloud API                        ║
║  3. Cloud checks if hash is in known malware database         ║
║  4. Result returned: known threat / unknown / benign          ║
║  5. Result cached locally for offline use                     ║
║                                                                ║
║  🔒 HASHES ARE ONE-WAY:                                       ║
║  • Cannot reverse hash to get file contents                   ║
║  • Hashes alone reveal nothing about the file                 ║
║  • Standard cryptographic practice                            ║
║                                                                ║
║  ✅ OFFLINE MODE ALWAYS AVAILABLE:                            ║
║  • Cloud sync is optional                                     ║
║  • HEX-AVG works perfectly without cloud sync                 ║
║  • You can disable cloud sync at any time                     ║
║  • Cached hashes available offline                            ║
║                                                                ║
║  📊 DATA RETENTION:                                           ║
║  • Hashes are not stored                                      ║
║  • No logging of queries                                      ║
║  • No tracking of users                                       ║
║  • Query results are ephemeral                                ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"""
    
    def _load_cache(self) -> Dict:
        """Load local cache of cloud queries"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'hashes': {},
            'last_sync': None,
            'version': '1.0'
        }
    
    def _save_cache(self):
        """Save cache to disk"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except:
            pass
    
    def enable(self, show_notice: bool = True):
        """
        Enable cloud sync (requires user opt-in)
        
        Args:
            show_notice: Show privacy notice before enabling
        """
        if show_notice:
            print(self.privacy_notice)
            
            consent = input("\nDo you want to enable cloud signature sync? (yes/no): ")
            if consent.lower() not in ['yes', 'y']:
                print("❌ Cloud sync remains disabled")
                return
        
        self.enabled = True
        print("✅ Cloud signature sync enabled")
        print("ℹ️  Only file hashes will be sent to the cloud - no file contents")
    
    def disable(self):
        """Disable cloud sync"""
        self.enabled = False
        print("✅ Cloud signature sync disabled")
        print("ℹ️  HEX-AVG will work in offline mode")
    
    def is_enabled(self) -> bool:
        """Check if cloud sync is enabled"""
        return self.enabled
    
    def query_hash(self, file_path: Path) -> Dict:
        """
        Query cloud database for file hash
        
        Args:
            file_path: Path to file to query
            
        Returns:
            Dict with query result
        """
        if not self.enabled:
            return {
                'status': 'disabled',
                'message': 'Cloud sync is disabled. Enable with: hex-avg cloud enable'
            }
        
        if self.offline_mode:
            return self._query_cache(file_path)
        
        # Calculate file hashes
        hashes = self._calculate_hashes(file_path)
        
        # Check cache first
        cache_result = self._query_cache(hashes['sha256'])
        if cache_result['status'] == 'found':
            return cache_result
        
        # Query cloud (simulated)
        cloud_result = self._query_cloud(hashes)
        
        # Cache result
        if cloud_result['status'] == 'success':
            self._cache_hash(hashes['sha256'], cloud_result)
        
        return cloud_result
    
    def _calculate_hashes(self, file_path: Path) -> Dict[str, str]:
        """Calculate file hashes"""
        hashes = {
            'md5': '',
            'sha1': '',
            'sha256': ''
        }
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            hashes['md5'] = hashlib.md5(content).hexdigest()
            hashes['sha1'] = hashlib.sha1(content).hexdigest()
            hashes['sha256'] = hashlib.sha256(content).hexdigest()
            
        except Exception as e:
            pass
        
        return hashes
    
    def _query_cache(self, hash_value: str) -> Dict:
        """Query local cache"""
        if hash_value in self.cache['hashes']:
            return {
                'status': 'found',
                'cached': True,
                'result': self.cache['hashes'][hash_value]
            }
        
        return {
            'status': 'not_found',
            'cached': True,
            'message': 'Hash not found in local cache'
        }
    
    def _query_cloud(self, hashes: Dict[str, str]) -> Dict:
        """
        Query cloud API (simulated)
        
        In production, this would make an actual HTTP request to your API
        """
        try:
            # Simulate cloud query
            # In production:
            # response = requests.post(
            #     self.api_endpoint,
            #     json={'sha256': hashes['sha256']},
            #     timeout=5
            # )
            # result = response.json()
            
            # For now, simulate responses based on hash
            result = self._simulate_cloud_response(hashes['sha256'])
            
            return {
                'status': 'success',
                'cloud': True,
                'result': result
            }
            
        except Exception as e:
            # Fall back to offline mode
            self.offline_mode = True
            return {
                'status': 'offline',
                'message': f'Cloud query failed: {str(e)}. Using offline mode.',
                'result': None
            }
    
    def _simulate_cloud_response(self, hash_value: str) -> Dict:
        """
        Simulate cloud API response
        
        This is for demonstration. In production, you would have
        an actual cloud database of malware hashes.
        """
        # Simulate some known malicious hashes
        known_malicious_hashes = {
            '0000000000000000000000000000000000000000000000000000000000000001': {
                'threat': 'Trojan.GenericKD.12345',
                'severity': 'high',
                'category': 'trojan',
                'first_seen': '2024-01-01',
                'detection_rate': '95/100'
            },
            '0000000000000000000000000000000000000000000000000000000000000002': {
                'threat': 'Worm.AutoRun.67890',
                'severity': 'critical',
                'category': 'worm',
                'first_seen': '2024-01-15',
                'detection_rate': '98/100'
            }
        }
        
        # Simulate some known benign hashes
        known_benign_hashes = {
            '1111111111111111111111111111111111111111111111111111111111111111': {
                'status': 'benign',
                'category': 'system',
                'first_seen': '2020-01-01'
            }
        }
        
        # Check if hash is known
        if hash_value in known_malicious_hashes:
            return {
                'status': 'malicious',
                'threat': known_malicious_hashes[hash_value]
            }
        elif hash_value in known_benign_hashes:
            return {
                'status': 'benign',
                'info': known_benign_hashes[hash_value]
            }
        else:
            return {
                'status': 'unknown',
                'message': 'Hash not found in cloud database'
            }
    
    def _cache_hash(self, hash_value: str, result: Dict):
        """Cache hash result"""
        self.cache['hashes'][hash_value] = result
        self._save_cache()
    
    def clear_cache(self):
        """Clear local cache"""
        self.cache['hashes'] = {}
        self._save_cache()
        print("✅ Cloud cache cleared")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'total_cached_hashes': len(self.cache['hashes']),
            'malicious_hashes': sum(
                1 for r in self.cache['hashes'].values()
                if isinstance(r, dict) and r.get('status') == 'malicious'
            ),
            'benign_hashes': sum(
                1 for r in self.cache['hashes'].values()
                if isinstance(r, dict) and r.get('status') == 'benign'
            ),
            'unknown_hashes': sum(
                1 for r in self.cache['hashes'].values()
                if isinstance(r, dict) and r.get('status') == 'unknown'
            ),
            'last_sync': self.cache['last_sync']
        }
    
    def set_offline_mode(self, offline: bool = True):
        """
        Set offline mode
        
        Args:
            offline: True to force offline mode, False to try cloud
        """
        self.offline_mode = offline
        status = "offline" if offline else "online"
        print(f"✅ Cloud sync set to {status} mode")


# Create global instance
_cloud_client = None


def get_cloud_client() -> CloudSyncClient:
    """Get global cloud client instance"""
    global _cloud_client
    if _cloud_client is None:
        _cloud_client = CloudSyncClient()
    return _cloud_client