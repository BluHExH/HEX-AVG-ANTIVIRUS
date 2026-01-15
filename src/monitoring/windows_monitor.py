"""
HEX-AVG Windows File Monitor
Implements real-time file monitoring using FileSystemWatcher
"""

import threading
import time
from pathlib import Path
from typing import List, Callable, Optional
import os

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Warning: watchdog not available - file monitoring disabled")

from config import HEXAVGConfig


class WindowsFileMonitor:
    """Real-time file monitoring for Windows"""
    
    def __init__(
        self,
        paths_to_watch: List[str],
        on_file_created: Optional[Callable] = None,
        on_file_modified: Optional[Callable] = None,
        on_file_deleted: Optional[Callable] = None
    ):
        """
        Initialize file monitor
        
        Args:
            paths_to_watch: List of paths to monitor
            on_file_created: Callback for file creation events
            on_file_modified: Callback for file modification events
            on_file_deleted: Callback for file deletion events
        """
        self.paths_to_watch = paths_to_watch
        self.on_file_created = on_file_created
        self.on_file_modified = on_file_modified
        self.on_file_deleted = on_file_deleted
        
        self.running = False
        self.observer = None
        self.monitor_thread = None
        
        # Statistics
        self.stats = {
            "events_processed": 0,
            "files_created": 0,
            "files_modified": 0,
            "files_deleted": 0,
            "errors": 0
        }
        
        # Check availability
        if not WATCHDOG_AVAILABLE:
            print("Error: watchdog library not available. Install with: pip install watchdog")
    
    def _validate_paths(self) -> List[Path]:
        """Validate and convert paths to Path objects"""
        valid_paths = []
        
        for path_str in self.paths_to_watch:
            try:
                path = Path(path_str).expanduser()
                
                if path.exists():
                    if path.is_dir():
                        valid_paths.append(path)
                    else:
                        print(f"Warning: {path} is not a directory, skipping")
                else:
                    print(f"Warning: {path} does not exist, skipping")
            
            except Exception as e:
                print(f"Error validating path {path_str}: {e}")
        
        return valid_paths
    
    def _create_event_handler(self):
        """Create FileSystemEventHandler"""
        class Handler(FileSystemEventHandler):
            def __init__(self, monitor):
                self.monitor = monitor
            
            def on_created(self, event: FileSystemEvent):
                """Handle file/directory creation"""
                if not event.is_directory:
                    self.monitor.stats['files_created'] += 1
                    self.monitor.stats['events_processed'] += 1
                    
                    if self.monitor.on_file_created:
                        try:
                            self.monitor.on_file_created(event.src_path)
                        except Exception as e:
                            self.monitor.stats['errors'] += 1
                            print(f"Error in file_created callback: {e}")
            
            def on_modified(self, event: FileSystemEvent):
                """Handle file/directory modification"""
                if not event.is_directory:
                    self.monitor.stats['files_modified'] += 1
                    self.monitor.stats['events_processed'] += 1
                    
                    if self.monitor.on_file_modified:
                        try:
                            self.monitor.on_file_modified(event.src_path)
                        except Exception as e:
                            self.monitor.stats['errors'] += 1
                            print(f"Error in file_modified callback: {e}")
            
            def on_deleted(self, event: FileSystemEvent):
                """Handle file/directory deletion"""
                if not event.is_directory:
                    self.monitor.stats['files_deleted'] += 1
                    self.monitor.stats['events_processed'] += 1
                    
                    if self.monitor.on_file_deleted:
                        try:
                            self.monitor.on_file_deleted(event.src_path)
                        except Exception as e:
                            self.monitor.stats['errors'] += 1
                            print(f"Error in file_deleted callback: {e}")
            
            def on_moved(self, event: FileSystemEvent):
                """Handle file/directory move/rename"""
                if not event.is_directory:
                    # Treat move as deletion + creation
                    if self.monitor.on_file_deleted:
                        try:
                            self.monitor.on_file_deleted(event.src_path)
                        except Exception as e:
                            print(f"Error in file_deleted (move) callback: {e}")
                    
                    if self.monitor.on_file_created:
                        try:
                            self.monitor.on_file_created(event.dest_path)
                        except Exception as e:
                            print(f"Error in file_created (move) callback: {e}")
        
        return Handler(self)
    
    def start(self) -> bool:
        """Start file monitoring"""
        if self.running:
            print("File monitor is already running")
            return False
        
        if not WATCHDOG_AVAILABLE:
            print("Cannot start file monitoring - watchdog not available")
            return False
        
        # Validate paths
        valid_paths = self._validate_paths()
        if not valid_paths:
            print("No valid paths to monitor")
            return False
        
        print(f"Starting file monitoring for {len(valid_paths)} path(s)...")
        
        try:
            # Create observer
            self.observer = Observer()
            handler = self._create_event_handler()
            
            # Schedule watches
            for path in valid_paths:
                self.observer.schedule(handler, str(path), recursive=True)
                print(f"  Watching: {path}")
            
            # Start observer
            self.observer.start()
            self.running = True
            
            print("File monitoring started successfully")
            return True
        
        except Exception as e:
            print(f"Error starting file monitor: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop file monitoring"""
        if not self.running:
            print("File monitor is not running")
            return False
        
        print("Stopping file monitoring...")
        
        try:
            if self.observer:
                self.observer.stop()
                self.observer.join(timeout=5)
            
            self.running = False
            print("File monitoring stopped successfully")
            return True
        
        except Exception as e:
            print(f"Error stopping file monitor: {e}")
            return False
    
    def get_statistics(self) -> dict:
        """Get monitoring statistics"""
        return self.stats.copy()
    
    def add_path(self, path: str) -> bool:
        """Add a path to monitor"""
        if not self.running:
            print("Cannot add path - monitor not running")
            return False
        
        try:
            path_obj = Path(path).expanduser()
            
            if not path_obj.exists():
                print(f"Path does not exist: {path}")
                return False
            
            if not path_obj.is_dir():
                print(f"Path is not a directory: {path}")
                return False
            
            # Add watch
            handler = self._create_event_handler()
            self.observer.schedule(handler, str(path_obj), recursive=True)
            
            print(f"Added watch for: {path}")
            return True
        
        except Exception as e:
            print(f"Error adding path: {e}")
            return False
    
    def remove_path(self, path: str) -> bool:
        """Remove a path from monitoring"""
        # Note: watchdog doesn't support removing individual watches
        # Need to restart monitor with updated path list
        print("Warning: Cannot remove individual watch. Restart monitor with updated path list.")
        return False
    
    def pause(self) -> None:
        """Pause monitoring (stop processing events)"""
        self.running = False
        print("File monitoring paused")
    
    def resume(self) -> None:
        """Resume monitoring"""
        if not self.running and self.observer:
            self.running = True
            print("File monitoring resumed")
    
    def get_status(self) -> dict:
        """Get monitor status"""
        status = {
            "running": self.running,
            "paths_watched": len(self._validate_paths()),
            "statistics": self.stats.copy()
        }
        return status


class SimpleFileMonitor:
    """Simple file monitor using polling (fallback if watchdog not available)"""
    
    def __init__(
        self,
        paths_to_watch: List[str],
        on_file_created: Optional[Callable] = None,
        on_file_modified: Optional[Callable] = None,
        poll_interval: int = 5
    ):
        """
        Initialize simple file monitor (polling-based)
        
        Args:
            paths_to_watch: List of paths to monitor
            on_file_created: Callback for file creation events
            on_file_modified: Callback for file modification events
            poll_interval: Polling interval in seconds
        """
        self.paths_to_watch = paths_to_watch
        self.on_file_created = on_file_created
        self.on_file_modified = on_file_modified
        self.poll_interval = poll_interval
        
        self.running = False
        self.monitor_thread = None
        self.file_states = {}
        
        print("Warning: Using polling-based file monitor (less efficient)")
    
    def _scan_directory(self, directory: Path) -> dict:
        """Scan directory and return file states"""
        file_states = {}
        
        try:
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    stat = file_path.stat()
                    file_states[str(file_path)] = {
                        'size': stat.st_size,
                        'modified': stat.st_mtime,
                        'exists': True
                    }
        except Exception as e:
            print(f"Error scanning directory {directory}: {e}")
        
        return file_states
    
    def _compare_states(self, old_states: dict, new_states: dict) -> None:
        """Compare old and new file states and trigger callbacks"""
        # Check for new files
        for path, state in new_states.items():
            if path not in old_states:
                if self.on_file_created:
                    self.on_file_created(path)
            else:
                # Check for modifications
                old_state = old_states[path]
                if (state['size'] != old_state['size'] or 
                    state['modified'] != old_state['modified']):
                    if self.on_file_modified:
                        self.on_file_modified(path)
        
        # Check for deleted files
        for path in old_states:
            if path not in new_states:
                if self.on_file_deleted:
                    self.on_file_deleted(path)
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Scan all paths
                new_states = {}
                for path_str in self.paths_to_watch:
                    path = Path(path_str).expanduser()
                    if path.exists() and path.is_dir():
                        new_states.update(self._scan_directory(path))
                
                # Compare and trigger callbacks
                self._compare_states(self.file_states, new_states)
                
                # Update states
                self.file_states = new_states
            
            except Exception as e:
                print(f"Error in monitor loop: {e}")
            
            # Wait before next poll
            time.sleep(self.poll_interval)
    
    def start(self) -> bool:
        """Start file monitoring"""
        if self.running:
            print("File monitor is already running")
            return False
        
        print(f"Starting polling file monitor (interval: {self.poll_interval}s)...")
        
        # Initialize file states
        self.file_states = {}
        for path_str in self.paths_to_watch:
            path = Path(path_str).expanduser()
            if path.exists() and path.is_dir():
                self.file_states.update(self._scan_directory(path))
        
        # Start monitoring thread
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print("File monitoring started successfully")
        return True
    
    def stop(self) -> bool:
        """Stop file monitoring"""
        if not self.running:
            print("File monitor is not running")
            return False
        
        print("Stopping file monitoring...")
        self.running = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        
        print("File monitoring stopped successfully")
        return True


def create_file_monitor(
    paths_to_watch: List[str],
    use_watchdog: bool = True,
    **callbacks
) -> object:
    """
    Factory function to create appropriate file monitor
    
    Args:
        paths_to_watch: List of paths to monitor
        use_watchdog: Try to use watchdog if available
        **callbacks: Callback functions (on_file_created, on_file_modified, on_file_deleted)
    
    Returns:
        File monitor instance
    """
    if use_watchdog and WATCHDOG_AVAILABLE:
        return WindowsFileMonitor(paths_to_watch, **callbacks)
    else:
        return SimpleFileMonitor(paths_to_watch, **callbacks)