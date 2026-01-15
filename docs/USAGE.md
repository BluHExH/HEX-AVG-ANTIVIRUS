# HEX-AVG Usage Guide

Complete usage instructions for HEX-AVG Antivirus.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Basic Commands](#basic-commands)
3. [Scanning](#scanning)
4. [Detection Methods](#detection-methods)
5. [Quarantine Management](#quarantine-management)
6. [Reporting](#reporting)
7. [Advanced Features](#advanced-features)
8. [Examples](#examples)
9. [Best Practices](#best-practices)

---

## Quick Start

### First Scan

```bash
# Linux
hex-avg scan /home/user/documents

# Windows
python hex_avg.py scan C:\Users\Username\Documents
```

### Quick Scan

```bash
# Skip archives for faster scanning
hex-avg scan --quick /tmp
```

### Update Signatures

```bash
hex-avg update
```

---

## Basic Commands

### Version Information

```bash
hex-avg --version
```

Output:
```
HEX-AVG v1.0.0 - Phoenix
Platform: LINUX
Python: 3.11.0
```

### Help

```bash
# General help
hex-avg --help

# Command-specific help
hex-avg scan --help
hex-avg quarantine --help
```

### Setup Check

```bash
hex-avg setup check
```

Output:
```
✓ Directories exist
✓ Threads valid
✓ File size valid
✓ Entropy valid
✓ Hash algorithms valid

All checks passed!
```

---

## Scanning

### Basic Scan

```bash
hex-avg scan /path/to/directory
```

### Quick Scan

Skips archive files for faster scanning:

```bash
hex-avg scan --quick /path/to/directory
```

### Full Scan

Comprehensive scan of all files:

```bash
hex-avg scan --full /path/to/directory
```

### Custom Thread Count

Control the number of threads for scanning:

```bash
# Use 4 threads
hex-avg scan --threads 4 /path/to/directory

# Use 16 threads
hex-avg scan --threads 16 /path/to/directory
```

### Enable Heuristic Analysis

```bash
hex-avg scan --heuristic /path/to/directory
```

### Enable YARA Rules (Linux Only)

```bash
hex-avg scan --yara /path/to/directory
```

### Dry Run Mode

Scan without making any changes:

```bash
hex-avg scan --dry-run /path/to/directory
```

### Progress Display

Show progress bar during scan:

```bash
hex-avg scan --progress /path/to/directory
```

### System-Wide Scans

```bash
# Full system scan
hex-avg scan --full

# Quick system scan
hex-avg scan --quick
```

---

## Detection Methods

### 1. Signature-Based Detection

Automatically enabled. HEX-AVG compares file hashes against a database of known malware signatures.

**How it works:**
- Calculates MD5, SHA1, and SHA256 hashes of each file
- Matches hashes against signature database
- Returns threat information if match found

**Output example:**
```
THREATS DETECTED:

File: /home/user/malware.exe
  - Type: signature, Name: Trojan.GenericKD.41234567, Severity: high
```

### 2. Heuristic Analysis

Detects suspicious files through pattern analysis:

```bash
hex-avg scan --heuristic /path
```

**Detects:**
- Suspicious file extensions
- Abnormal file sizes
- Double file extensions
- High/low entropy (packed/encrypted files)

**Output example:**
```
THREATS DETECTED:

File: /home/user/suspicious.doc.exe
  - Type: double_extension, Name: Double extension detected, Severity: high
  - Type: high_entropy, Name: High entropy (7.8): possible packing, Severity: high
```

### 3. YARA Rules (Linux Only)

Advanced pattern matching with custom rules:

```bash
hex-avg scan --yara /path
```

**Supported YARA rule categories:**
- EICAR test detection
- Packer detection
- PowerShell malicious patterns
- Base64 encoding detection
- Registry modification attempts

---

## Quarantine Management

### Quarantine a File

```bash
hex-avg quarantine add /path/to/malware.exe
```

### List Quarantined Files

```bash
hex-avg quarantine list
```

Output:
```
ID  File Path                           Quarantine Date    Size
1   /home/user/malware.exe             2024-01-01 10:30  1.2 MB
2   /home/user/suspicious.dll          2024-01-01 11:45  256 KB
```

### Restore from Quarantine

```bash
hex-avg quarantine restore 1
```

### Delete from Quarantine

```bash
hex-avg quarantine delete 1
```

### Clear All Quarantined Files

```bash
hex-avg quarantine clear
```

---

## Reporting

### Generate JSON Report

```bash
hex-avg report --json --output scan_report.json
```

### Generate HTML Report

```bash
hex-avg report --html --output scan_report.html
```

### Generate CSV Report

```bash
hex-avg report --csv --output scan_report.csv
```

### Generate Text Report

```bash
hex-avg report --output scan_report.txt
```

### Report Contents

Reports include:
- Scan summary (files scanned, threats found, duration)
- List of detected threats
- File hashes
- Timestamps
- System information

---

## Advanced Features

### File Analysis

Analyze a single file in detail:

```bash
# Basic analysis
hex-avg analyze /path/to/file.exe

# Deep analysis
hex-avg analyze --deep /path/to/file.exe

# Calculate entropy
hex-avg analyze --entropy /path/to/file.exe

# PE file analysis (Windows)
hex-avg analyze --pe /path/to/file.exe

# ELF file analysis (Linux)
hex-avg analyze --elf /path/to/file
```

### Logs Management

View and export logs:

```bash
# View recent logs
hex-avg logs --tail

# View specific number of lines
hex-avg logs --tail 50

# Export logs
hex-avg logs --export audit.log

# Clear logs
hex-avg logs --clear
```

### Benchmark Testing

Test HEX-AVG performance and detection capabilities:

```bash
# Run all benchmarks
hex-avg benchmark

# Test EICAR detection
hex-avg benchmark --test-eicar
```

### Cache Management

Clean cache and temporary files:

```bash
hex-avg clean
```

---

## Examples

### Example 1: Basic Document Scan

```bash
hex-avg scan ~/Documents
```

Output:
```
============================================================
HEX-AVG Scanner v1.0.0
============================================================
Scan Path: /home/user/Documents
Scan Type: Full
Threads: 8
Heuristics: Enabled
YARA Rules: Disabled
============================================================

Discovering files...
Found 1,234 files to scan

Starting scan...
Scanning files: 1234/1234 (100.0%)

============================================================
SCAN SUMMARY
============================================================
Files Scanned: 1234
Files Skipped: 12
Threats Found: 0
Scan Duration: 45.23 seconds
============================================================

✓ Scan completed! No threats found.
```

### Example 2: Detecting Malware

```bash
hex-avg scan --heuristic ~/Downloads
```

Output:
```
============================================================
SCAN SUMMARY
============================================================
Files Scanned: 89
Files Skipped: 3
Threats Found: 2
Scan Duration: 12.45 seconds
============================================================

THREATS DETECTED:

File: /home/user/Downloads/suspicious.exe
  - Type: signature, Name: Trojan.GenericKD.41234567, Severity: high
  - Type: high_entropy, Name: High entropy (7.9): possible packing, Severity: high

File: /home/user/Downloads/evil.doc.exe
  - Type: double_extension, Name: Double extension detected, Severity: high

⚠ Scan completed! 2 threats found!
```

### Example 3: Full System Scan

```bash
hex-avg scan --full --progress
```

This will scan all system directories with progress display.

### Example 4: Custom Scan with Options

```bash
hex-avg scan \
  --heuristic \
  --yara \
  --threads 16 \
  --progress \
  /home/user/projects
```

This scan:
- Enables heuristic analysis
- Enables YARA rules
- Uses 16 threads
- Shows progress
- Scans the projects directory

### Example 5: Quarantine Workflow

```bash
# Scan and quarantine
hex-avg scan /tmp

# If threats found, quarantine them
hex-avg quarantine add /tmp/malware.exe

# List quarantined files
hex-avg quarantine list

# Restore if false positive
hex-avg quarantine restore 1
```

---

## Best Practices

### 1. Regular Scanning

```bash
# Schedule weekly full scans
# Use cron on Linux
0 2 * * 0 /usr/local/bin/hex-avg scan --full /home/user

# Use Task Scheduler on Windows
```

### 2. Keep Signatures Updated

```bash
# Update before important scans
hex-avg update
hex-avg scan --full
```

### 3. Use Appropriate Scan Types

```bash
# Quick scan for routine checks
hex-avg scan --quick ~/Documents

# Full scan for security audits
hex-avg scan --full /home/user

# Heuristic scan for unknown threats
hex-avg scan --heuristic ~/Downloads
```

### 4. Monitor Logs

```bash
# Regularly check logs for suspicious activity
hex-avg logs --tail 100

# Export logs for analysis
hex-avg logs --export weekly_audit.log
```

### 5. Test Detection Capabilities

```bash
# Regularly test with EICAR
hex-avg benchmark --test-eicar

# Run performance benchmarks
hex-avg benchmark
```

### 6. Quarantine Management

```bash
# Regularly review quarantined files
hex-avg quarantine list

# Delete confirmed malware
hex-avg quarantine delete <id>

# Restore false positives
hex-avg quarantine restore <id>
```

### 7. Resource Management

```bash
# Adjust thread count based on system
hex-avg scan --threads 4 /path  # For older systems
hex-avg scan --threads 16 /path # For modern systems

# Use quick scan when time is limited
hex-avg scan --quick /path
```

### 8. Reporting

```bash
# Generate reports after important scans
hex-avg scan --full
hex-avg report --json --output scan_$(date +%Y%m%d).json
hex-avg report --html --output scan_$(date +%Y%m%d).html
```

---

## Performance Tips

### Optimize Scan Speed

```bash
# Use quick scan for routine checks
hex-avg scan --quick /path

# Adjust thread count
hex-avg scan --threads 16 /path

# Skip unnecessary directories
hex-avg scan /home/user/Documents --exclude=/home/user/Documents/Archives
```

### Reduce Memory Usage

```bash
# Use fewer threads
hex-avg scan --threads 4 /path

# Scan specific directories instead of full system
hex-avg scan /home/user/Downloads
```

---

## Troubleshooting

### Scan Fails

```bash
# Check file permissions
ls -la /path/to/directory

# Run with dry-run mode
hex-avg scan --dry-run /path

# Check logs
hex-avg logs --tail
```

### False Positives

```bash
# Analyze the file
hex-avg analyze --deep /path/to/file

# Check file hashes
hex-avg analyze /path/to/file

# Restore from quarantine if needed
hex-avg quarantine restore <id>
```

### Performance Issues

```bash
# Reduce thread count
hex-avg scan --threads 4 /path

# Use quick scan
hex-avg scan --quick /path

# Check system resources
top  # Linux
Task Manager  # Windows
```

---

## Integration Examples

### Bash Script for Automated Scanning

```bash
#!/bin/bash
# automated_scan.sh

DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="scan_$DATE.log"
REPORT_FILE="report_$DATE.json"

echo "Starting automated scan at $DATE"

# Update signatures
hex-avg update

# Perform scan
hex-avg scan --full /home/user > $LOG_FILE 2>&1

# Generate report
hex-avg report --json --output $REPORT_FILE

# Send notification (if threats found)
if grep -q "Threats Found: [1-9]" $LOG_FILE; then
    echo "⚠ THREATS DETECTED! Check $LOG_FILE"
else
    echo "✓ Scan complete - no threats found"
fi
```

### PowerShell Script for Automated Scanning

```powershell
# automated_scan.ps1

$Date = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = "scan_$Date.log"
$ReportFile = "report_$Date.json"

Write-Host "Starting automated scan at $Date"

# Update signatures
python hex_avg.py update

# Perform scan
python hex_avg.py scan --full C:\Users\Username | Out-File $LogFile

# Generate report
python hex_avg.py report --json --output $ReportFile

# Check for threats
if (Select-String -Path $LogFile -Pattern "Threats Found: [1-9]") {
    Write-Host "⚠ THREATS DETECTED! Check $LogFile"
} else {
    Write-Host "✓ Scan complete - no threats found"
}
```

---

## Additional Resources

- [Installation Guide](INSTALLATION.md)
- [Development Roadmap](../HEX-AVG_ROADMAP.md)
- [GitHub Repository](https://github.com/yourusername/hex-avg)
- [Issue Tracker](https://github.com/yourusername/hex-avg/issues)

---

**Last Updated**: 2024-01-01  
**Version**: 1.0.0