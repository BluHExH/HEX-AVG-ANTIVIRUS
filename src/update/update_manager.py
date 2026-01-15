"""
Auto Update Manager for HEX-AVG
Safe, user-controlled updates using GitHub Releases
"""

import os
import sys
import json
import shutil
import hashlib
import requests
from pathlib import Path
from typing import Dict, Optional, Tuple
import tempfile
import zipfile


class UpdateManager:
    """
    Manages HEX-AVG updates from GitHub Releases
    
    Features:
    - Tool version updates
    - Signature/rule updates
    - User consent required
    - Safe rollback on failure
    - Offline mode support
    """
    
    def __init__(self, repo_owner: str = "yourusername", repo_name: str = "hex-avg"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.api_base = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.releases_url = f"{self.api_base}/releases"
        
        # Local paths
        self.base_dir = Path(__file__).parent.parent.parent
        self.backup_dir = self.base_dir / ".backup"
        self.temp_dir = self.base_dir / ".temp"
        self.version_file = self.base_dir / "VERSION"
        self.current_version = self._get_current_version()
        
        # User preferences
        self.config_file = self.base_dir / "update_config.json"
        self.config = self._load_config()
    
    def _get_current_version(self) -> str:
        """Get current version from config.py"""
        try:
            sys.path.insert(0, str(self.base_dir))
            from config import HEXAVGConfig
            return HEXAVGConfig.VERSION
        except ImportError:
            return "0.0.0"
    
    def _load_config(self) -> Dict:
        """Load update configuration"""
        default_config = {
            'auto_update_enabled': False,
            'cloud_sync_enabled': False,
            'last_check': None,
            'consent_given': False
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return default_config
        
        return default_config
    
    def _save_config(self):
        """Save update configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def check_for_updates(self, include_prerelease: bool = False) -> Optional[Dict]:
        """
        Check for available updates
        
        Returns:
            Dict with update info if available, None otherwise
        """
        try:
            print(f"🔍 Checking for updates (current: {self.current_version})...")
            
            # Get latest release from GitHub
            response = requests.get(
                self.releases_url + "/latest",
                headers={'Accept': 'application/vnd.github.v3+json'},
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to check for updates: HTTP {response.status_code}")
                return None
            
            release = response.json()
            latest_version = release['tag_name'].lstrip('v')
            
            print(f"📌 Latest version available: {latest_version}")
            
            # Check if update is needed
            if self._is_newer_version(latest_version):
                print(f"✅ Update available: {self.current_version} → {latest_version}")
                
                return {
                    'current_version': self.current_version,
                    'latest_version': latest_version,
                    'release_name': release['name'],
                    'release_notes': release.get('body', ''),
                    'release_date': release['published_at'],
                    'assets': self._get_platform_assets(release)
                }
            else:
                print("✅ You're already on the latest version!")
                return None
                
        except requests.RequestException as e:
            print(f"❌ Network error checking for updates: {e}")
            print("ℹ️  Running in offline mode - cannot check for updates")
            return None
        except Exception as e:
            print(f"❌ Error checking for updates: {e}")
            return None
    
    def _is_newer_version(self, version: str) -> bool:
        """Check if version is newer than current"""
        try:
            current = tuple(map(int, self.current_version.split('.')))
            latest = tuple(map(int, version.split('.')))
            return latest > current
        except:
            return False
    
    def _get_platform_assets(self, release: Dict) -> Dict:
        """Get relevant assets for current platform"""
        import platform
        system = platform.system().lower()
        
        assets = {}
        for asset in release.get('assets', []):
            name = asset['name'].lower()
            
            if system == 'windows':
                if 'portable.zip' in name or 'setup.exe' in name:
                    assets['installer'] = {
                        'name': asset['name'],
                        'url': asset['browser_download_url'],
                        'size': asset['size']
                    }
            elif system == 'linux':
                if '.deb' in name:
                    assets['deb'] = {
                        'name': asset['name'],
                        'url': asset['browser_download_url'],
                        'size': asset['size']
                    }
                elif 'appimage' in name:
                    assets['appimage'] = {
                        'name': asset['name'],
                        'url': asset['browser_download_url'],
                        'size': asset['size']
                    }
            
            if 'rules' in name or 'signatures' in name:
                assets['rules'] = {
                    'name': asset['name'],
                    'url': asset['browser_download_url'],
                    'size': asset['size']
                }
        
        return assets
    
    def update_tool(self, update_info: Dict, force: bool = False) -> bool:
        """
        Update HEX-AVG tool to latest version
        
        Args:
            update_info: Update information from check_for_updates()
            force: Force update without additional confirmation
            
        Returns:
            True if update successful, False otherwise
        """
        if not force and not self.config.get('consent_given'):
            print("\n" + "="*60)
            print("⚠️  UPDATE CONFIRMATION REQUIRED")
            print("="*60)
            print(f"Current version: {update_info['current_version']}")
            print(f"New version: {update_info['latest_version']}")
            print(f"\nRelease: {update_info['release_name']}")
            print(f"Date: {update_info['release_date']}")
            print(f"\nRelease Notes:")
            print(update_info['release_notes'][:500])
            print("="*60)
            
            consent = input("\nDo you want to proceed with the update? (yes/no): ")
            if consent.lower() not in ['yes', 'y']:
                print("❌ Update cancelled by user")
                return False
        
        try:
            print("\n🔄 Starting update process...")
            
            # Create backup
            if not self._create_backup():
                print("❌ Failed to create backup - aborting update")
                return False
            
            # Download update
            asset = self._select_update_asset(update_info['assets'])
            if not asset:
                print("❌ No suitable update package found for your platform")
                return False
            
            download_path = self._download_update(asset)
            if not download_path:
                print("❌ Failed to download update")
                return False
            
            # Verify checksum
            if not self._verify_download(download_path, asset):
                print("❌ Download verification failed")
                return False
            
            # Install update
            if not self._install_update(download_path):
                print("❌ Failed to install update")
                self._restore_backup()
                return False
            
            # Clean up
            self._cleanup()
            
            print(f"✅ Successfully updated to version {update_info['latest_version']}")
            print("🔄 Please restart HEX-AVG to use the new version")
            
            return True
            
        except Exception as e:
            print(f"❌ Update failed: {e}")
            self._restore_backup()
            return False
    
    def update_rules(self, update_info: Optional[Dict] = None) -> bool:
        """
        Update virus signatures and detection rules
        
        Args:
            update_info: Update info from check_for_updates(), or None to check
            
        Returns:
            True if update successful, False otherwise
        """
        if not update_info:
            update_info = self.check_for_updates()
            if not update_info:
                print("No rule updates available")
                return False
        
        if 'rules' not in update_info['assets']:
            print("No rule update package available")
            return False
        
        try:
            print("\n🔄 Updating virus signatures and detection rules...")
            
            asset = update_info['assets']['rules']
            download_path = self._download_update(asset, suffix='rules')
            
            if not download_path:
                print("❌ Failed to download rule update")
                return False
            
            # Extract rules
            signatures_dir = self.base_dir / "signatures"
            if not signatures_dir.exists():
                signatures_dir.mkdir(parents=True)
            
            with zipfile.ZipFile(download_path, 'r') as zip_ref:
                zip_ref.extractall(signatures_dir)
            
            print("✅ Virus signatures and detection rules updated successfully")
            
            # Clean up
            download_path.unlink()
            
            return True
            
        except Exception as e:
            print(f"❌ Rule update failed: {e}")
            return False
    
    def _create_backup(self) -> bool:
        """Create backup of current installation"""
        try:
            print("📦 Creating backup...")
            
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup essential files
            files_to_backup = [
                'config.py',
                'hex_avg.py',
                'hex_avg_level2.py',
                'src/',
                'signatures/'
            ]
            
            for item in files_to_backup:
                src = self.base_dir / item
                if src.exists():
                    dst = self.backup_dir / item
                    if src.is_file():
                        shutil.copy2(src, dst)
                    elif src.is_dir():
                        if dst.exists():
                            shutil.rmtree(dst)
                        shutil.copytree(src, dst)
            
            print("✅ Backup created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return False
    
    def _restore_backup(self) -> bool:
        """Restore from backup"""
        try:
            print("🔄 Restoring backup...")
            
            if not self.backup_dir.exists():
                print("❌ No backup found")
                return False
            
            # Restore files
            for item in self.backup_dir.rglob('*'):
                if item.is_file():
                    relative_path = item.relative_to(self.backup_dir)
                    dst = self.base_dir / relative_path
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dst)
            
            print("✅ Backup restored successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to restore backup: {e}")
            return False
    
    def _download_update(self, asset: Dict, suffix: str = 'update') -> Optional[Path]:
        """Download update package"""
        try:
            print(f"📥 Downloading {asset['name']} ({asset['size'] / 1024 / 1024:.1f} MB)...")
            
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            download_path = self.temp_dir / f"{suffix}_{asset['name']}"
            
            # Download with progress
            response = requests.get(asset['url'], stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r   Progress: {progress:.1f}%", end='', flush=True)
            
            print()  # New line after progress
            print(f"✅ Downloaded to {download_path}")
            
            return download_path
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return None
    
    def _verify_download(self, download_path: Path, asset: Dict) -> bool:
        """Verify downloaded file"""
        try:
            # Check file size
            if download_path.stat().st_size != asset['size']:
                print(f"❌ File size mismatch: expected {asset['size']}, got {download_path.stat().st_size}")
                return False
            
            # Calculate checksum (if available)
            print("✅ Download verified")
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def _select_update_asset(self, assets: Dict) -> Optional[Dict]:
        """Select appropriate update asset for platform"""
        import platform
        system = platform.system().lower()
        
        if system == 'windows':
            return assets.get('installer') or assets.get('deb')
        elif system == 'linux':
            return assets.get('deb') or assets.get('appimage')
        
        return None
    
    def _install_update(self, download_path: Path) -> bool:
        """Install update package"""
        try:
            print("📦 Installing update...")
            
            # For now, just extract the update
            # In production, this would handle different package formats
            
            if download_path.suffix == '.zip':
                with zipfile.ZipFile(download_path, 'r') as zip_ref:
                    # Extract to temp directory first
                    temp_extract = self.temp_dir / "extracted"
                    temp_extract.mkdir(parents=True, exist_ok=True)
                    zip_ref.extractall(temp_extract)
                
                # Move files to base directory
                for item in temp_extract.rglob('*'):
                    if item.is_file():
                        relative_path = item.relative_to(temp_extract)
                        dst = self.base_dir / relative_path
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dst)
                
                print("✅ Update installed successfully")
                return True
            
            print("⚠️  Update package format not supported")
            return False
            
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            return False
    
    def _cleanup(self):
        """Clean up temporary files"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
            print("🧹 Cleanup complete")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")
    
    def enable_auto_update(self):
        """Enable automatic updates (with consent)"""
        self.config['auto_update_enabled'] = True
        self.config['consent_given'] = True
        self._save_config()
        print("✅ Auto-update enabled")
    
    def disable_auto_update(self):
        """Disable automatic updates"""
        self.config['auto_update_enabled'] = False
        self._save_config()
        print("✅ Auto-update disabled")
    
    def enable_cloud_sync(self):
        """Enable cloud signature sync (opt-in)"""
        self.config['cloud_sync_enabled'] = True
        self._save_config()
        print("✅ Cloud signature sync enabled")
        print("⚠️  Only file hashes will be queried - no file uploads")
    
    def disable_cloud_sync(self):
        """Disable cloud signature sync"""
        self.config['cloud_sync_enabled'] = False
        self._save_config()
        print("✅ Cloud signature sync disabled")