"""
HEX-AVG Persistence Detection Module
Detects persistence mechanisms on Windows and Linux
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from config import HEXAVGConfig


class PersistenceDetector:
    """Detects persistence mechanisms on the system"""
    
    def __init__(self):
        """Initialize persistence detector"""
        self.detected_persistence = []
        self.alerts = []
        
        # Platform-specific detection
        if HEXAVGConfig.IS_WINDOWS:
            self.detector = WindowsPersistenceDetector()
        elif HEXAVGConfig.IS_LINUX:
            self.detector = LinuxPersistenceDetector()
        else:
            self.detector = None
    
    def scan(self) -> Dict[str, Any]:
        """
        Scan for persistence mechanisms
        
        Returns:
            Scan results dictionary
        """
        if not self.detector:
            return {
                "platform": HEXAVGConfig.PLATFORM,
                "status": "not_supported",
                "persistence_found": [],
                "alerts": []
            }
        
        results = self.detector.scan()
        
        # Store results
        self.detected_persistence = results.get('persistence_found', [])
        self.alerts = results.get('alerts', [])
        
        # Log findings
        self._log_findings(results)
        
        return results
    
    def _log_findings(self, results: Dict[str, Any]) -> None:
        """Log persistence findings"""
        log_file = HEXAVGConfig.LOGS_DIR / "persistence.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] Persistence Scan Results\n")
            f.write(f"  Total persistence found: {len(results.get('persistence_found', []))}\n")
            f.write(f"  Alerts generated: {len(results.get('alerts', []))}\n")
            
            for alert in results.get('alerts', []):
                f.write(f"  [{alert['severity'].upper()}] {alert['message']}\n")
            
            f.write("\n")
    
    def get_persistence_list(self) -> List[Dict[str, Any]]:
        """Get list of detected persistence mechanisms"""
        return self.detected_persistence.copy()
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get list of alerts"""
        return self.alerts.copy()
    
    def clear(self) -> None:
        """Clear detection results"""
        self.detected_persistence = []
        self.alerts = []


class WindowsPersistenceDetector:
    """Detects Windows persistence mechanisms"""
    
    def __init__(self):
        """Initialize Windows persistence detector"""
        self.registry_keys = [
            "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
            "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
            "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
            "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
            "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\\Run",
            "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\\Run"
        ]
        
        self.startup_folders = [
            Path(Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"),
            Path("C:/ProgramData/Microsoft/Windows/Start Menu/Programs/Startup")
        ]
    
    def scan(self) -> Dict[str, Any]:
        """Scan for Windows persistence mechanisms"""
        results = {
            "platform": "windows",
            "status": "completed",
            "persistence_found": [],
            "alerts": []
        }
        
        # Scan Registry Run keys
        registry_persistence = self._scan_registry_run_keys()
        results['persistence_found'].extend(registry_persistence)
        
        # Scan Startup folders
        startup_persistence = self._scan_startup_folders()
        results['persistence_found'].extend(startup_persistence)
        
        # Scan Scheduled Tasks
        task_persistence = self._scan_scheduled_tasks()
        results['persistence_found'].extend(task_persistence)
        
        # Analyze findings and generate alerts
        alerts = self._analyze_persistence(results['persistence_found'])
        results['alerts'] = alerts
        
        return results
    
    def _scan_registry_run_keys(self) -> List[Dict[str, Any]]:
        """Scan Registry Run keys (READ-ONLY)"""
        persistence = []
        
        try:
            import winreg
            
            for key_path in self.registry_keys:
                try:
                    # Parse registry key path
                    root_key, sub_key = self._parse_registry_path(key_path)
                    
                    # Open registry key (READ-ONLY)
                    with winreg.OpenKey(root_key, sub_key) as key:
                        # Enumerate values
                        i = 0
                        while True:
                            try:
                                name, value, _ = winreg.EnumValue(key, i)
                                
                                persistence.append({
                                    "type": "registry_run_key",
                                    "location": key_path,
                                    "name": name,
                                    "value": value,
                                    "suspicious": self._is_suspicious_registry_entry(name, value)
                                })
                                
                                i += 1
                            except WindowsError:
                                break
                
                except Exception as e:
                    # Registry key may not exist or access denied
                    continue
        
        except ImportError:
            print("Warning: winreg not available")
        except Exception as e:
            print(f"Error scanning registry: {e}")
        
        return persistence
    
    def _parse_registry_path(self, path: str):
        """Parse registry key path"""
        import winreg
        
        if path.startswith("HKLM\&quot;):
            return winreg.HKEY_LOCAL_MACHINE, path[5:]
        elif path.startswith("HKCU\&quot;):
            return winreg.HKEY_CURRENT_USER, path[5:]
        else:
            raise ValueError(f"Unknown registry root: {path}")
    
    def _is_suspicious_registry_entry(self, name: str, value: str) -> bool:
        """Check if registry entry is suspicious"""
        # Suspicious indicators
        suspicious_extensions = ['.exe', '.bat', '.cmd', '.ps1', '.vbs', '.js']
        suspicious_locations = ['temp', 'appdata', 'downloads', 'public']
        
        value_lower = value.lower()
        
        # Check for suspicious extensions
        for ext in suspicious_extensions:
            if ext in value_lower:
                return True
        
        # Check for suspicious locations
        for loc in suspicious_locations:
            if loc in value_lower:
                return True
        
        # Check for obfuscated paths
        if '%' in value or '~' in value:
            return True
        
        return False
    
    def _scan_startup_folders(self) -> List[Dict[str, Any]]:
        """Scan Startup folders"""
        persistence = []
        
        for folder in self.startup_folders:
            if not folder.exists():
                continue
            
            try:
                for file_path in folder.glob('*'):
                    if file_path.is_file():
                        persistence.append({
                            "type": "startup_folder",
                            "location": str(folder),
                            "file": file_path.name,
                            "path": str(file_path),
                            "suspicious": self._is_suspicious_startup_file(file_path)
                        })
            
            except Exception as e:
                print(f"Error scanning startup folder {folder}: {e}")
        
        return persistence
    
    def _is_suspicious_startup_file(self, file_path: Path) -> bool:
        """Check if startup file is suspicious"""
        # Suspicious extensions
        suspicious_extensions = ['.exe', '.bat', '.cmd', '.ps1', '.vbs', '.js']
        
        if file_path.suffix.lower() in suspicious_extensions:
            return True
        
        # Check if file is in temp or downloads
        path_lower = str(file_path).lower()
        if 'temp' in path_lower or 'downloads' in path_lower:
            return True
        
        return False
    
    def _scan_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """Scan Scheduled Tasks (READ-ONLY)"""
        persistence = []
        
        try:
            # Use PowerShell to get scheduled tasks
            result = subprocess.run(
                ['powershell', '-Command', 'Get-ScheduledTask | ConvertTo-Json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                tasks = json.loads(result.stdout)
                
                for task in tasks:
                    if isinstance(task, dict):
                        task_name = task.get('TaskName', '')
                        task_state = task.get('State', '')
                        
                        # Check if task is enabled
                        if task_state == 'Ready' or task_state == 'Running':
                            persistence.append({
                                "type": "scheduled_task",
                                "name": task_name,
                                "state": task_state,
                                "suspicious": self._is_suspicious_scheduled_task(task)
                            })
        
        except Exception as e:
            print(f"Error scanning scheduled tasks: {e}")
        
        return persistence
    
    def _is_suspicious_scheduled_task(self, task: Dict[str, Any]) -> bool:
        """Check if scheduled task is suspicious"""
        task_name = task.get('TaskName', '').lower()
        task_path = task.get('TaskPath', '').lower()
        
        # Suspicious indicators
        suspicious_keywords = ['update', 'updater', 'install', 'download', 'temp']
        
        for keyword in suspicious_keywords:
            if keyword in task_name or keyword in task_path:
                return True
        
        return False
    
    def _analyze_persistence(self, persistence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze persistence mechanisms and generate alerts"""
        alerts = []
        
        # Count suspicious entries
        suspicious_count = sum(1 for p in persistence if p.get('suspicious', False))
        
        if suspicious_count > 0:
            alerts.append({
                "severity": "high",
                "message": f"Found {suspicious_count} suspicious persistence mechanism(s)",
                "count": suspicious_count
            })
        
        # Check for unusual persistence in temp folders
        temp_persistence = [p for p in persistence if 'temp' in str(p.get('location', '')).lower()]
        if temp_persistence:
            alerts.append({
                "severity": "medium",
                "message": f"Found {len(temp_persistence)} persistence mechanism(s) in temporary folders",
                "count": len(temp_persistence)
            })
        
        return alerts


class LinuxPersistenceDetector:
    """Detects Linux persistence mechanisms"""
    
    def __init__(self):
        """Initialize Linux persistence detector"""
        self.autostart_paths = [
            Path.home() / ".config/autostart",
            Path.home() / ".config/autostart.sh",
            Path("/etc/xdg/autostart")
        ]
        
        self.service_paths = [
            Path.home() / ".config/systemd/user",
            Path("/etc/systemd/system")
        ]
    
    def scan(self) -> Dict[str, Any]:
        """Scan for Linux persistence mechanisms"""
        results = {
            "platform": "linux",
            "status": "completed",
            "persistence_found": [],
            "alerts": []
        }
        
        # Scan systemd services
        service_persistence = self._scan_systemd_services()
        results['persistence_found'].extend(service_persistence)
        
        # Scan crontab
        crontab_persistence = self._scan_crontab()
        results['persistence_found'].extend(crontab_persistence)
        
        # Scan autostart files
        autostart_persistence = self._scan_autostart_files()
        results['persistence_found'].extend(autostart_persistence)
        
        # Analyze findings and generate alerts
        alerts = self._analyze_persistence(results['persistence_found'])
        results['alerts'] = alerts
        
        return results
    
    def _scan_systemd_services(self) -> List[Dict[str, Any]]:
        """Scan systemd user services (READ-ONLY)"""
        persistence = []
        
        try:
            # List user services
            result = subprocess.run(
                ['systemctl', '--user', 'list-unit-files', '--type=service'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'loaded' in line and 'enabled' in line:
                        service_name = line.split()[0]
                        
                        persistence.append({
                            "type": "systemd_service",
                            "name": service_name,
                            "suspicious": self._is_suspicious_service(service_name)
                        })
        
        except Exception as e:
            print(f"Error scanning systemd services: {e}")
        
        return persistence
    
    def _is_suspicious_service(self, service_name: str) -> bool:
        """Check if service is suspicious"""
        # Suspicious indicators
        suspicious_keywords = ['update', 'updater', 'download', 'temp']
        
        for keyword in suspicious_keywords:
            if keyword in service_name.lower():
                return True
        
        return False
    
    def _scan_crontab(self) -> List[Dict[str, Any]]:
        """Scan user crontab (READ-ONLY)"""
        persistence = []
        
        try:
            result = subprocess.run(
                ['crontab', '-l'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                
                for i, line in enumerate(lines, 1):
                    # Skip comments and empty lines
                    if line.startswith('#') or not line.strip():
                        continue
                    
                    persistence.append({
                        "type": "crontab",
                        "line": line,
                        "line_number": i,
                        "suspicious": self._is_suspicious_crontab_entry(line)
                    })
        
        except Exception as e:
            # User may not have crontab
            pass
        
        return persistence
    
    def _is_suspicious_crontab_entry(self, line: str) -> bool:
        """Check if crontab entry is suspicious"""
        # Suspicious indicators
        suspicious_keywords = ['wget', 'curl', 'download', 'temp', '/dev/shm']
        
        line_lower = line.lower()
        
        for keyword in suspicious_keywords:
            if keyword in line_lower:
                return True
        
        return False
    
    def _scan_autostart_files(self) -> List[Dict[str, Any]]:
        """Scan autostart files (READ-ONLY)"""
        persistence = []
        
        for path in self.autostart_paths:
            if not path.exists():
                continue
            
            try:
                if path.is_file():
                    # Scan single autostart file
                    persistence.append({
                        "type": "autostart_file",
                        "path": str(path),
                        "suspicious": self._is_suspicious_autostart_file(path)
                    })
                
                elif path.is_dir():
                    # Scan directory for .desktop files
                    for file_path in path.glob('*.desktop'):
                        persistence.append({
                            "type": "autostart_desktop",
                            "file": file_path.name,
                            "path": str(file_path),
                            "suspicious": self._is_suspicious_autostart_file(file_path)
                        })
            
            except Exception as e:
                print(f"Error scanning autostart path {path}: {e}")
        
        return persistence
    
    def _is_suspicious_autostart_file(self, file_path: Path) -> bool:
        """Check if autostart file is suspicious"""
        # Suspicious indicators
        suspicious_extensions = ['.sh', '.py', '.pl', '.rb']
        
        if file_path.suffix in suspicious_extensions:
            return True
        
        # Check file content
        try:
            content = file_path.read_text().lower()
            
            if 'wget' in content or 'curl' in content:
                return True
            
            if 'temp' in content or '/dev/shm' in content:
                return True
        
        except Exception:
            pass
        
        return False
    
    def _analyze_persistence(self, persistence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze persistence mechanisms and generate alerts"""
        alerts = []
        
        # Count suspicious entries
        suspicious_count = sum(1 for p in persistence if p.get('suspicious', False))
        
        if suspicious_count > 0:
            alerts.append({
                "severity": "high",
                "message": f"Found {suspicious_count} suspicious persistence mechanism(s)",
                "count": suspicious_count
            })
        
        return alerts