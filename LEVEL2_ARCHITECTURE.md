# HEX-AVG LEVEL-2 Architecture
## Background Security Protector

---

## 🎯 LEVEL-2 Overview

HEX-AVG LEVEL-2 transforms the manual scanner into a **background security assistant** that provides real-time protection without kernel drivers or destructive system changes.

### Core Philosophy
- **User-Space Only**: All operations in user space
- **Non-Destructive**: Read-only operations where possible
- **Coexistence**: Works alongside Windows Defender/Linux security
- **Educational**: Defensive security focus
- **Safe**: No system file deletion or modification

---

## 🏗️ Updated Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     HEX-AVG LEVEL-2 SYSTEM                          │
└─────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐  ┌────────▼────────┐  ┌────────▼────────┐
│   CLI Client   │  │  Background     │  │  Scheduler     │
│   (hex-avg)    │  │  Service        │  │  Daemon        │
└────────┬───────┘  └────────┬────────┘  └────────┬────────┘
         │                  │                  │
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
        ┌─────▼────┐  ┌────▼────┐  ┌────▼────────┐
        │  Core    │  │Monitor  │  │ Persistence │
        │  Scanner │  │Engine   │  │  Detector   │
        └─────┬────┘  └────┬────┘  └────┬────────┘
              │            │            │
              └────────────┼────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐      ┌─────▼──────┐     ┌────▼────┐
   │Detection │      │ Quarantine │     │ Alert   │
   │ Engines  │      │ Manager    │     │ System  │
   └──────────┘      └────────────┘     └─────────┘
```

---

## 🔄 Component Overview

### 1. Background Service / Daemon

#### Windows Implementation
```python
# Background Service (Windows)
- Runs as Windows Service or persistent PowerShell task
- Auto-start on boot (user-approved)
- Manages file monitoring and scheduled scans
- Handles service lifecycle (start/stop/restart)
- Communicates with CLI via named pipes or sockets
```

#### Linux Implementation
```python
# Background Daemon (systemd)
- Runs as systemd user service
- Auto-start on user login
- Manages inotify file monitoring
- Handles scheduled scans via cron integration
- Communicates with CLI via Unix socket
```

### 2. Real-Time File Monitoring

#### Monitor High-Risk Locations
```
Windows:
- %USERPROFILE%\Downloads
- %USERPROFILE%\Desktop
- %TEMP%
- %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
- USB mount points (E:\, F:\, etc.)

Linux:
- ~/Downloads
- ~/Desktop
- /tmp
- ~/.config/autostart
- USB mount points (/media/*)
```

#### File System Events
```python
# Events to monitor
- File Created: Scan immediately
- File Modified: Re-scan if executable
- File Moved: Check new location
- File Deleted: Remove from quarantine (if applicable)
```

### 3. Scheduled Scanning

```python
# Schedule Configuration
{
    "daily_scan": {
        "enabled": true,
        "time": "02:00",
        "paths": ["~/Documents", "~/Downloads"],
        "mode": "quick"
    },
    "weekly_scan": {
        "enabled": true,
        "day": "Sunday",
        "time": "03:00",
        "paths": ["/home/user"],
        "mode": "full"
    }
}
```

### 4. Persistence Detection

#### Windows Persistence Mechanisms
```python
# Registry Keys (READ-ONLY)
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce
HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce

# Startup Folders (READ-ONLY)
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs\Startup

# Scheduled Tasks (READ-ONLY)
Get-ScheduledTask -TaskPath "\*&quot;
```

#### Linux Persistence Mechanisms
```python
# Systemd Services (READ-ONLY)
systemctl --user list-unit-files --type=service
cat ~/.config/systemd/user/*.service

# Crontab (READ-ONLY)
crontab -l
cat /etc/cron.d/*

# Autostart Files (READ-ONLY)
~/.config/autostart/*.desktop
~/.config/autostart.sh
```

### 5. Process-Level Protection

```python
# Process Monitoring (User-Space)
- Monitor process creation events
- Scan executable before execution
- Check hash against threat database
- Apply heuristic analysis
- Block suspicious processes (ask user first)
```

### 6. Enhanced Quarantine System

```python
# Secure Quarantine
- Isolated directory with restricted permissions
- Encrypted file storage
- Metadata preservation (original path, timestamp)
- Restore capability
- Audit logging
```

### 7. Alert & Notification System

```python
# Alert Severity Levels
- CRITICAL: Immediate action required
- HIGH: Threat detected, user attention needed
- MEDIUM: Suspicious activity detected
- LOW: Informational message
- INFO: Normal operation

# Notification Channels
- CLI alerts
- System notifications (Windows toast, Linux desktop)
- Log file with timestamps
- Email alerts (optional)
```

---

## 🛡️ Security Model

### Threats HEX-AVG LEVEL-2 CAN Stop

1. **Malicious Executables**
   - Downloaded malware executables
   - Suspicious scripts (PowerShell, bash)
   - Packed/obfuscated malware

2. **Persistence Mechanisms**
   - Unauthorized startup entries
   - Suspicious scheduled tasks
   - Malicious services/daemons

3. **File-Based Threats**
   - EICAR test virus (verification)
   - Known malware signatures
   - Heuristically suspicious files

4. **Process-Based Threats**
   - Suspicious process launches
   - Executables with malicious hashes
   - High-entropy executables

### Threats HEX-AVG LEVEL-2 CANNOT Stop

1. **Kernel-Level Rootkits**
   - Requires kernel drivers for detection
   - HEX-AVG is user-space only

2. **In-Memory Attacks**
   - Code injection into legitimate processes
   - Memory-only malware

3. **Network Attacks**
   - Drive-by downloads (before file creation)
   - Network-based exploits

4. **Advanced Persistence**
   - WMI event subscriptions (Windows)
   - Kernel module persistence (Linux)

5. **Living off the Land**
   - Using legitimate system tools maliciously
   - LOLBins (Windows)

---

## 🔧 Technical Implementation

### Background Service Implementation

#### Windows Service Structure
```python
# src/services/windows_service.py
class HEXAVGWindowsService:
    def __init__(self):
        self.name = "HEXAVGBackgroundService"
        self.display_name = "HEX-AVG Background Protector"
        self.description = "HEX-AVG Real-time Protection Service"
        self.running = False
    
    def start(self):
        """Start the background service"""
        self.running = True
        # Start file monitoring
        # Start scheduler
        # Start process monitoring
    
    def stop(self):
        """Stop the background service"""
        self.running = False
        # Stop all monitoring
        # Stop scheduler
    
    def status(self):
        """Get service status"""
        return {
            "running": self.running,
            "start_time": self.start_time,
            "files_scanned": self.files_scanned,
            "threats_blocked": self.threats_blocked
        }
```

#### Linux Systemd Service Structure
```python
# src/services/linux_daemon.py
class HEXAVGLinuxDaemon:
    def __init__(self):
        self.name = "hex-avg-daemon"
        self.pid_file = "/var/run/hex-avg.pid"
        self.running = False
    
    def start(self):
        """Start the daemon"""
        self.running = True
        # Start inotify monitoring
        # Start scheduler
        # Start process monitoring
    
    def stop(self):
        """Stop the daemon"""
        self.running = False
        # Stop all monitoring
        # Clean up
    
    def status(self):
        """Get daemon status"""
        return {
            "running": self.running,
            "pid": self.get_pid(),
            "uptime": self.get_uptime()
        }
```

### File Monitoring Implementation

#### Windows FileSystemWatcher
```python
# src/monitoring/windows_monitor.py
class WindowsFileMonitor:
    def __init__(self, paths_to_watch):
        self.paths_to_watch = paths_to_watch
        self.watcher = threading.Thread(target=self._monitor_loop)
    
    def _monitor_loop(self):
        """Monitor file system changes"""
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        class Handler(FileSystemEventHandler):
            def on_created(self, event):
                if not event.is_directory:
                    # Scan created file
                    scan_file(event.src_path)
            
            def on_modified(self, event):
                if not event.is_directory:
                    # Check if executable and re-scan
                    if is_executable(event.src_path):
                        scan_file(event.src_path)
        
        observer = Observer()
        observer.schedule(Handler(), self.paths_to_watch, recursive=True)
        observer.start()
```

#### Linux inotify Monitor
```python
# src/monitoring/linux_monitor.py
class LinuxFileMonitor:
    def __init__(self, paths_to_watch):
        self.paths_to_watch = paths_to_watch
        self.inotify = pyinotify.INotify()
    
    def _monitor_loop(self):
        """Monitor file system changes using inotify"""
        class Handler(pyinotify.ProcessEvent):
            def process_IN_CREATE(self, event):
                # Scan created file
                scan_file(event.pathname)
            
            def process_IN_MODIFY(self, event):
                # Check if executable and re-scan
                if is_executable(event.pathname):
                    scan_file(event.pathname)
        
        mask = pyinotify.IN_CREATE | pyinotify.IN_MODIFY
        watch_manager = pyinotify.WatchManager()
        watch_manager.add_watch(self.paths_to_watch, mask, rec=True)
        notifier = pyinotify.Notifier(watch_manager, Handler())
        notifier.loop()
```

---

## 📋 Updated CLI Commands

### Background Management
```bash
hex-avg start              # Start background protection
hex-avg stop               # Stop background protection
hex-avg restart            # Restart background service
hex-avg status             # Show protection status
hex-avg enable-autostart   # Enable auto-start on boot
hex-avg disable-autostart  # Disable auto-start on boot
```

### Scanning
```bash
hex-avg scan <path>        # Manual scan
hex-avg quick-scan <path>  # Quick scan
hex-avg full-scan <path>   # Full scan
```

### Scheduling
```bash
hex-avg schedule           # View current schedule
hex-avg schedule set       # Configure scan schedule
hex-avg schedule clear     # Clear schedule
```

### Quarantine
```bash
hex-avg quarantine list    # List quarantined files
hex-avg quarantine add     # Quarantine file
hex-avg quarantine restore # Restore file
hex-avg quarantine delete  # Delete quarantined file
```

### Logs & Alerts
```bash
hex-avg logs               # View security logs
hex-avg logs --tail 50     # View recent logs
hex-avg alerts             # View recent alerts
hex-avg alerts --clear     # Clear alerts
```

---

## 🔒 Security & Safety Rules

### Mandatory Safety Measures
1. **User-Space Only**: No kernel drivers or hooks
2. **Read-Only Registry**: Only read Windows Registry
3. **No System Deletion**: Never delete system files
4. **Coexistence**: Work alongside existing AV software
5. **Explicit Permission**: Ask before blocking executables
6. **Audit Logging**: Log all actions for transparency
7. **Educational Focus**: Defensive security only

### Defensive Use Only
- ✅ Detect and alert on threats
- ✅ Quarantine suspicious files
- ✅ Monitor persistence mechanisms
- ✅ Provide security insights
- ❌ No offensive capabilities
- ❌ No system modification
- ❌ No destructive actions

---

## 📊 Performance Considerations

### Resource Usage
- **Memory**: ~100-200MB (background service)
- **CPU**: <1% idle, spikes during file operations
- **Disk I/O**: Minimal, event-driven monitoring
- **Network**: None (offline operation)

### Optimization Strategies
- **Event-Driven**: React to file system events
- **Smart Scanning**: Only scan executables
- **Caching**: Cache file hashes
- **Low-Priority**: Run with low CPU priority
- **Throttling**: Limit scan rate during system load

---

## 🎯 LEVEL-2 Success Criteria

### Functional Requirements
- ✅ Background service runs continuously
- ✅ Real-time file monitoring works
- ✅ Scheduled scans execute on schedule
- ✅ Persistence detection identifies threats
- ✅ Process monitoring detects suspicious launches
- ✅ Quarantine system isolates threats
- ✅ Alert system notifies users

### Non-Functional Requirements
- ✅ Low resource consumption
- ✅ Stable operation (no crashes)
- ✅ Coexists with existing security software
- ✅ User-friendly CLI interface
- ✅ Comprehensive logging
- ✅ Safe operation (no system damage)

---

## 🔄 Upgrade Path from LEVEL-1

### What Changes
1. **Add background service/daemon**
2. **Add file monitoring system**
3. **Add scheduling engine**
4. **Add persistence detection**
5. **Add process monitoring**
6. **Enhance quarantine system**
7. **Add alert system**

### What Stays the Same
1. **Core scanning engine** (unchanged)
2. **Detection engines** (unchanged)
3. **Configuration system** (unchanged)
4. **CLI structure** (extended)

---

## 📝 Implementation Plan

### Phase 1: Background Service (Week 1)
- Create Windows Service implementation
- Create Linux systemd daemon
- Implement service lifecycle management

### Phase 2: File Monitoring (Week 1-2)
- Implement Windows FileSystemWatcher
- Implement Linux inotify monitoring
- Add high-risk location monitoring

### Phase 3: Scheduled Scanning (Week 2)
- Create scheduling engine
- Implement daily/weekly schedules
- Add low-resource scan mode

### Phase 4: Persistence Detection (Week 2-3)
- Implement Windows persistence scanning
- Implement Linux persistence scanning
- Create alert system for persistence

### Phase 5: Process Monitoring (Week 3)
- Implement process monitoring
- Add executable-on-execution scanning
- Create user approval system

### Phase 6: Enhanced Quarantine (Week 3)
- Improve quarantine isolation
- Add encryption
- Implement restore functionality

### Phase 7: CLI Updates (Week 4)
- Add background management commands
- Add schedule configuration
- Update help system

### Phase 8: Testing & Documentation (Week 4)
- Test all features
- Write LEVEL-2 documentation
- Create installation guides
- Test coexistence with existing AV

---

**HEX-AVG LEVEL-2 - Background Security Protector**  
*Real-time Protection | User-Space | Safe | Educational*