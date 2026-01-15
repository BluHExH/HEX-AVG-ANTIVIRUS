"""
HEX-AVG Scan Scheduler
Implements scheduled scanning for background protection
"""

import time
import threading
import json
import schedule
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from config import HEXAVGConfig


class ScanScheduler:
    """Scheduled scan manager"""
    
    def __init__(
        self,
        scanner,
        config: Dict[str, Any] = None,
        low_resource_mode: bool = True
    ):
        """
        Initialize scan scheduler
        
        Args:
            scanner: HEXAVGScanner instance
            config: Schedule configuration
            low_resource_mode: Enable low-resource mode
        """
        self.scanner = scanner
        self.config = config or {}
        self.low_resource_mode = low_resource_mode
        
        self.running = False
        self.scheduler_thread = None
        self.stop_event = threading.Event()
        
        # Statistics
        self.stats = {
            "scheduled_scans_run": 0,
            "total_files_scanned": 0,
            "threats_found": 0,
            "last_scan_time": None
        }
        
        # Log directory
        self.log_dir = HEXAVGConfig.LOGS_DIR
        self.log_file = self.log_dir / "scheduled_scans.log"
    
    def configure_daily_scan(
        self,
        enabled: bool = True,
        scan_time: str = "02:00",
        paths: List[str] = None,
        mode: str = "quick"
    ) -> bool:
        """
        Configure daily scheduled scan
        
        Args:
            enabled: Enable daily scan
            scan_time: Time to run scan (HH:MM format)
            paths: List of paths to scan
            mode: Scan mode (quick/full)
        """
        try:
            if "scheduled_scans" not in self.config:
                self.config["scheduled_scans"] = {}
            
            self.config["scheduled_scans"]["daily"] = {
                "enabled": enabled,
                "time": scan_time,
                "paths": paths or [],
                "mode": mode
            }
            
            self._log_schedule_change("daily", enabled, scan_time)
            return True
        
        except Exception as e:
            print(f"Error configuring daily scan: {e}")
            return False
    
    def configure_weekly_scan(
        self,
        enabled: bool = True,
        day: str = "Sunday",
        scan_time: str = "03:00",
        paths: List[str] = None,
        mode: str = "full"
    ) -> bool:
        """
        Configure weekly scheduled scan
        
        Args:
            enabled: Enable weekly scan
            day: Day of week (Sunday, Monday, etc.)
            scan_time: Time to run scan (HH:MM format)
            paths: List of paths to scan
            mode: Scan mode (quick/full)
        """
        try:
            if "scheduled_scans" not in self.config:
                self.config["scheduled_scans"] = {}
            
            self.config["scheduled_scans"]["weekly"] = {
                "enabled": enabled,
                "day": day,
                "time": scan_time,
                "paths": paths or [],
                "mode": mode
            }
            
            self._log_schedule_change("weekly", enabled, f"{day} {scan_time}")
            return True
        
        except Exception as e:
            print(f"Error configuring weekly scan: {e}")
            return False
    
    def _log_schedule_change(self, scan_type: str, enabled: bool, time_str: str):
        """Log schedule configuration change"""
        status = "enabled" if enabled else "disabled"
        self._log(f"{scan_type.capitalize()} scan {status} for {time_str}")
    
    def start(self) -> bool:
        """Start the scheduler"""
        if self.running:
            print("Scheduler is already running")
            return False
        
        print("Starting scan scheduler...")
        self.running = True
        self.stop_event.clear()
        
        # Configure scheduled jobs
        self._configure_scheduled_jobs()
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            daemon=True
        )
        self.scheduler_thread.start()
        
        print("Scan scheduler started successfully")
        return True
    
    def stop(self) -> bool:
        """Stop the scheduler"""
        if not self.running:
            print("Scheduler is not running")
            return False
        
        print("Stopping scan scheduler...")
        self.running = False
        self.stop_event.set()
        
        # Clear all scheduled jobs
        schedule.clear()
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=10)
        
        print("Scan scheduler stopped successfully")
        return True
    
    def _configure_scheduled_jobs(self) -> None:
        """Configure scheduled scan jobs"""
        scheduled_scans = self.config.get("scheduled_scans", {})
        
        # Configure daily scan
        daily_config = scheduled_scans.get("daily", {})
        if daily_config.get("enabled", False):
            scan_time = daily_config.get("time", "02:00")
            schedule.every().day.at(scan_time).do(
                self._run_daily_scan,
                paths=daily_config.get("paths", []),
                mode=daily_config.get("mode", "quick")
            )
            print(f"  Daily scan scheduled for {scan_time}")
        
        # Configure weekly scan
        weekly_config = scheduled_scans.get("weekly", {})
        if weekly_config.get("enabled", False):
            scan_time = weekly_config.get("time", "03:00")
            day = weekly_config.get("day", "Sunday")
            
            # Get schedule attribute for day
            day_schedule = getattr(schedule.every(), day.lower(), None)
            if day_schedule:
                day_schedule.at(scan_time).do(
                    self._run_weekly_scan,
                    paths=weekly_config.get("paths", []),
                    mode=weekly_config.get("mode", "full")
                )
                print(f"  Weekly scan scheduled for {day} at {scan_time}")
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop"""
        while self.running and not self.stop_event.is_set():
            try:
                # Run pending scheduled jobs
                schedule.run_pending()
                
                # Wait before next check
                time.sleep(60)  # Check every minute
            
            except Exception as e:
                print(f"Error in scheduler loop: {e}")
                self._log(f"Scheduler error: {str(e)}")
    
    def _run_daily_scan(self, paths: List[str], mode: str) -> None:
        """Run daily scheduled scan"""
        if not self.running:
            return
        
        self._log(f"Starting daily {mode} scan")
        print(f"\n[SCHEDULED] Starting daily {mode} scan at {datetime.now()}")
        
        self._run_scheduled_scan(paths, mode, "daily")
    
    def _run_weekly_scan(self, paths: List[str], mode: str) -> None:
        """Run weekly scheduled scan"""
        if not self.running:
            return
        
        self._log(f"Starting weekly {mode} scan")
        print(f"\n[SCHEDULED] Starting weekly {mode} scan at {datetime.now()}")
        
        self._run_scheduled_scan(paths, mode, "weekly")
    
    def _run_scheduled_scan(self, paths: List[str], mode: str, scan_type: str) -> None:
        """Run scheduled scan"""
        if not paths:
            self._log(f"{scan_type.capitalize()} scan: No paths configured")
            print(f"[SCHEDULED] No paths configured for scan")
            return
        
        try:
            # Configure scanner for low-resource mode
            if self.low_resource_mode:
                self.scanner.threads = 2  # Use fewer threads
            
            total_files = 0
            total_threats = 0
            
            # Scan each path
            for path_str in paths:
                path = Path(path_str).expanduser()
                
                if not path.exists():
                    self._log(f"Path not found: {path}")
                    continue
                
                # Perform scan
                if mode == "quick":
                    result = self.scanner.quick_scan(path)
                else:
                    result = self.scanner.full_scan(path)
                
                total_files += result.get('files_scanned', 0)
                total_threats += result.get('threats_found', 0)
            
            # Update statistics
            self.stats['scheduled_scans_run'] += 1
            self.stats['total_files_scanned'] += total_files
            self.stats['threats_found'] += total_threats
            self.stats['last_scan_time'] = datetime.now().isoformat()
            
            # Log results
            self._log(
                f"{scan_type.capitalize()} scan completed: "
                f"{total_files} files scanned, {total_threats} threats found"
            )
            print(
                f"[SCHEDULED] {scan_type.capitalize()} scan completed: "
                f"{total_files} files scanned, {total_threats} threats found"
            )
            
            # Send alert if threats found
            if total_threats > 0:
                self._send_alert(
                    f"Scheduled scan detected {total_threats} threat(s)",
                    severity="high"
                )
        
        except Exception as e:
            print(f"Error during scheduled scan: {e}")
            self._log(f"Scheduled scan error: {str(e)}")
    
    def _log(self, message: str) -> None:
        """Log message to scheduled scans log"""
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().isoformat()
            with open(self.log_file, 'a') as f:
                f.write(f"[{timestamp}] {message}\n")
        
        except Exception as e:
            print(f"Error writing to log: {e}")
    
    def _send_alert(self, message: str, severity: str = "medium") -> None:
        """Send alert for scheduled scan findings"""
        # Write to alerts log
        alert_file = self.log_dir / "alerts.log"
        
        timestamp = datetime.now().isoformat()
        with open(alert_file, 'a') as f:
            f.write(f"[{timestamp}] [{severity.upper()}] SCHEDULED_SCAN: {message}\n")
        
        # Print alert
        print(f"[ALERT] Scheduled Scan: {message}")
    
    def get_schedule(self) -> Dict[str, Any]:
        """Get current schedule configuration"""
        return self.config.get("scheduled_scans", {})
    
    def get_next_run_time(self) -> Optional[str]:
        """Get next scheduled run time"""
        next_run = schedule.next_run()
        if next_run:
            return next_run.isoformat()
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get scheduler statistics"""
        stats = self.stats.copy()
        stats['next_run_time'] = self.get_next_run_time()
        stats['running'] = self.running
        return stats
    
    def clear_schedule(self) -> None:
        """Clear all scheduled scans"""
        schedule.clear()
        self.config["scheduled_scans"] = {
            "daily": {"enabled": False},
            "weekly": {"enabled": False}
        }
        self._log("All scheduled scans cleared")
        print("All scheduled scans cleared")
    
    def run_scan_now(self, scan_type: str = "daily") -> bool:
        """Run scheduled scan immediately"""
        try:
            if scan_type == "daily":
                daily_config = self.config.get("scheduled_scans", {}).get("daily", {})
                self._run_daily_scan(
                    paths=daily_config.get("paths", []),
                    mode=daily_config.get("mode", "quick")
                )
            elif scan_type == "weekly":
                weekly_config = self.config.get("scheduled_scans", {}).get("weekly", {})
                self._run_weekly_scan(
                    paths=weekly_config.get("paths", []),
                    mode=weekly_config.get("mode", "full")
                )
            else:
                print(f"Unknown scan type: {scan_type}")
                return False
            
            return True
        
        except Exception as e:
            print(f"Error running scan now: {e}")
            return False