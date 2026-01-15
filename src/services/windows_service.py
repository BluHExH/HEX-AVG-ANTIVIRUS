"""
HEX-AVG Windows Background Service
Implements Windows Service for background protection
"""

import time
import threading
import json
from pathlib import Path
from typing import Dict, Any, Optional
import sys

try:
    import pywin32system
    import win32service
    import win32serviceutil
    import win32event
    import servicemanager
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("Warning: pywin32 not available - running in console mode")

from config import HEXAVGConfig
from src.core import HEXAVGScanner
from src.monitoring.windows_monitor import WindowsFileMonitor
from src.scheduler.scan_scheduler import ScanScheduler


class HEXAVGWindowsService:
    """HEX-AVG Windows Background Service"""
    
    def __init__(self):
        """Initialize the Windows service"""
        self.name = "HEXAVGBackgroundService"
        self.display_name = "HEX-AVG Background Protector"
        self.description = "HEX-AVG Real-time Protection Service"
        
        self.running = False
        self.paused = False
        self.stop_event = threading.Event()
        
        # Configuration
        self.config_dir = HEXAVGConfig.BASE_DIR / "config"
        self.config_file = self.config_dir / "service_config.json"
        self.pid_file = HEXAVGConfig.BASE_DIR / "service.pid"
        
        # Components
        self.scanner = None
        self.file_monitor = None
        self.scheduler = None
        self.alert_system = None
        
        # Statistics
        self.stats = {
            "start_time": None,
            "files_scanned": 0,
            "threats_blocked": 0,
            "persistence_detected": 0,
            "uptime": 0
        }
        
        # Initialize
        self._load_config()
    
    def _load_config(self) -> None:
        """Load service configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = self._default_config()
                self._save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        import os
        
        return {
            "autostart": False,
            "monitor_downloads": True,
            "monitor_desktop": True,
            "monitor_temp": True,
            "monitor_usb": True,
            "scheduled_scans": {
                "daily": {
                    "enabled": False,
                    "time": "02:00",
                    "mode": "quick"
                },
                "weekly": {
                    "enabled": False,
                    "day": "Sunday",
                    "time": "03:00",
                    "mode": "full"
                }
            },
            "watch_paths": [
                os.path.expanduser("~/Downloads"),
                os.path.expanduser("~/Desktop"),
                os.environ.get("TEMP", "C:\\Windows\\Temp")
            ],
            "scan_on_create": True,
            "scan_on_modify": True,
            "block_suspicious": False,
            "alert_level": "high"
        }
    
    def _save_config(self) -> None:
        """Save service configuration"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def start(self) -> bool:
        """Start the background service"""
        if self.running:
            print("Service is already running")
            return False
        
        print(f"Starting {self.display_name}...")
        self.running = True
        self.stats['start_time'] = time.time()
        
        # Write PID file
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
        
        # Initialize components
        try:
            self._initialize_components()
            
            # Start monitoring
            self._start_monitoring()
            
            # Start scheduler
            self._start_scheduler()
            
            print(f"{self.display_name} started successfully")
            return True
        
        except Exception as e:
            print(f"Error starting service: {e}")
            self.running = False
            return False
    
    def stop(self) -> bool:
        """Stop the background service"""
        if not self.running:
            print("Service is not running")
            return False
        
        print(f"Stopping {self.display_name}...")
        self.running = False
        self.stop_event.set()
        
        # Stop components
        try:
            self._stop_monitoring()
            self._stop_scheduler()
        except Exception as e:
            print(f"Error stopping components: {e}")
        
        # Remove PID file
        if self.pid_file.exists():
            self.pid_file.unlink()
        
        print(f"{self.display_name} stopped successfully")
        return True
    
    def restart(self) -> bool:
        """Restart the service"""
        print("Restarting service...")
        self.stop()
        time.sleep(2)
        return self.start()
    
    def status(self) -> Dict[str, Any]:
        """Get service status"""
        if self.running:
            self.stats['uptime'] = time.time() - self.stats['start_time']
        
        status = {
            "running": self.running,
            "status": "Running" if self.running else "Stopped",
            "start_time": self.stats['start_time'],
            "uptime": self.stats['uptime'],
            "stats": self.stats.copy(),
            "config": {
                "monitoring": {
                    "downloads": self.config.get("monitor_downloads", False),
                    "desktop": self.config.get("monitor_desktop", False),
                    "temp": self.config.get("monitor_temp", False),
                    "usb": self.config.get("monitor_usb", False)
                },
                "scheduled_scans": self.config.get("scheduled_scans", {})
            }
        }
        
        return status
    
    def _initialize_components(self) -> None:
        """Initialize service components"""
        # Initialize scanner
        self.scanner = HEXAVGScanner(
            threads=4,  # Use fewer threads for background service
            enable_heuristics=True,
            enable_yara=False  # Disable YARA for performance
        )
        
        # Initialize file monitor
        watch_paths = self.config.get("watch_paths", [])
        self.file_monitor = WindowsFileMonitor(
            paths_to_watch=watch_paths,
            on_file_created=self._on_file_created,
            on_file_modified=self._on_file_modified
        )
        
        # Initialize scheduler
        self.scheduler = ScanScheduler(
            scanner=self.scanner,
            config=self.config.get("scheduled_scans", {})
        )
    
    def _start_monitoring(self) -> None:
        """Start file monitoring"""
        if self.file_monitor:
            self.file_monitor.start()
    
    def _stop_monitoring(self) -> None:
        """Stop file monitoring"""
        if self.file_monitor:
            self.file_monitor.stop()
    
    def _start_scheduler(self) -> None:
        """Start scan scheduler"""
        if self.scheduler:
            self.scheduler.start()
    
    def _stop_scheduler(self) -> None:
        """Stop scan scheduler"""
        if self.scheduler:
            self.scheduler.stop()
    
    def _on_file_created(self, file_path: str) -> None:
        """Handle file creation event"""
        if not self.running or self.paused:
            return
        
        try:
            # Check if file should be scanned
            if not self._should_scan_file(file_path):
                return
            
            print(f"[MONITOR] New file detected: {file_path}")
            
            # Scan the file
            result = self._scan_file(file_path)
            
            if result['threats_found'] > 0:
                self.stats['threats_blocked'] += 1
                self._send_alert("File Threat", f"Threat detected in {file_path}", "high")
        
        except Exception as e:
            print(f"Error handling file creation: {e}")
    
    def _on_file_modified(self, file_path: str) -> None:
        """Handle file modification event"""
        if not self.running or self.paused:
            return
        
        try:
            # Only scan if configured and file is executable
            if not self.config.get("scan_on_modify", False):
                return
            
            if not self._is_executable(file_path):
                return
            
            print(f"[MONITOR] File modified: {file_path}")
            
            # Scan the file
            result = self._scan_file(file_path)
            
            if result['threats_found'] > 0:
                self.stats['threats_blocked'] += 1
                self._send_alert("File Threat", f"Threat detected in modified file {file_path}", "high")
        
        except Exception as e:
            print(f"Error handling file modification: {e}")
    
    def _should_scan_file(self, file_path: str) -> bool:
        """Check if file should be scanned"""
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            return False
        
        # Check file size
        file_size = path.stat().st_size
        if file_size > HEXAVGConfig.MAX_SCAN_FILE_SIZE:
            return False
        
        # Check if executable
        if not self._is_executable(file_path):
            return False
        
        return True
    
    def _is_executable(self, file_path: str) -> bool:
        """Check if file is executable"""
        import os
        
        # Check extension
        path = Path(file_path)
        ext = path.suffix.lower()
        
        executable_extensions = [
            '.exe', '.dll', '.sys', '.bat', '.cmd', '.ps1', 
            '.vbs', '.js', '.jar', '.scr', '.pif', '.com'
        ]
        
        return ext in executable_extensions
    
    def _scan_file(self, file_path: str) -> Dict[str, Any]:
        """Scan a single file"""
        try:
            path = Path(file_path)
            
            # Quick scan
            result = self.scanner.quick_scan(path)
            
            self.stats['files_scanned'] += 1
            
            return result
        
        except Exception as e:
            print(f"Error scanning file {file_path}: {e}")
            return {'threats_found': 0}
    
    def _send_alert(self, title: str, message: str, severity: str) -> None:
        """Send alert notification"""
        # Log alert
        log_file = HEXAVGConfig.LOGS_DIR / "alerts.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        import datetime
        timestamp = datetime.datetime.now().isoformat()
        
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] [{severity.upper()}] {title}: {message}\n")
        
        # Print alert to console
        print(f"[ALERT] {severity.upper()}: {message}")
        
        # TODO: Implement system notification (Windows toast)
    
    def run(self) -> None:
        """Run the service main loop"""
        if not self.running:
            return
        
        print(f"{self.display_name} is running...")
        print("Press Ctrl+C to stop")
        
        try:
            while self.running and not self.stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nReceived interrupt signal")
            self.stop()
    
    def configure(self, **kwargs) -> bool:
        """Configure service"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
        
        self._save_config()
        
        # Restart monitoring if paths changed
        if 'watch_paths' in kwargs:
            if self.running:
                self._stop_monitoring()
                self._initialize_components()
                self._start_monitoring()
        
        return True


# Console mode wrapper for testing
class ConsoleServiceWrapper:
    """Wrapper for running service in console mode"""
    
    def __init__(self):
        self.service = HEXAVGWindowsService()
    
    def run(self):
        """Run service in console mode"""
        if self.service.start():
            self.service.run()
        else:
            print("Failed to start service")


# Main entry point
if __name__ == '__main__':
    import os
    
    # Check if running as Windows Service or console
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        service = HEXAVGWindowsService()
        
        if command == 'start':
            service.start()
        elif command == 'stop':
            service.stop()
        elif command == 'restart':
            service.restart()
        elif command == 'status':
            status = service.status()
            print(json.dumps(status, indent=2))
        else:
            print("Usage: python windows_service.py [start|stop|restart|status]")
    else:
        # Run in console mode
        wrapper = ConsoleServiceWrapper()
        wrapper.run()