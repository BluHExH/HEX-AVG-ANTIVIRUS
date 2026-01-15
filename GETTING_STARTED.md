# HEX-AVG - Quick Start Guide

Get started with HEX-AVG Antivirus in 5 minutes!

---

## 🚀 Quick Start (Linux)

### Step 1: Install

```bash
# Clone the repository
git clone https://github.com/yourusername/hex-avg.git
cd hex-avg

# Run the installation script
chmod +x scripts/install_linux.sh
sudo ./scripts/install_linux.sh
```

### Step 2: Verify

```bash
hex-avg --version
hex-avg setup check
```

### Step 3: First Scan

```bash
hex-avg scan ~/Documents
```

### Step 4: Test Detection

```bash
hex-avg benchmark --test-eicar
```

---

## 🪟 Quick Start (Windows)

### Step 1: Install Python

Download Python 3.11+ from [python.org](https://www.python.org/downloads/) and install with "Add to PATH" checked.

### Step 2: Download HEX-AVG

Download and extract HEX-AVG to `C:\hex-avg`

### Step 3: Install Dependencies

```powershell
cd C:\hex-avg
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 4: Initialize

```powershell
python hex_avg.py setup init
```

### Step 5: First Scan

```powershell
python hex_avg.py scan C:\Users\YourName\Documents
```

---

## 📋 Common Commands

### Scanning

```bash
# Basic scan
hex-avg scan /path/to/directory

# Quick scan (skip archives)
hex-avg scan --quick /path

# Full scan
hex-avg scan --full /path

# With heuristic analysis
hex-avg scan --heuristic /path

# With YARA rules (Linux)
hex-avg scan --yara /path

# Custom thread count
hex-avg scan --threads 16 /path
```

### Updates & Maintenance

```bash
# Update signatures
hex-avg update

# Check setup
hex-avg setup check

# Clean cache
hex-avg clean
```

### Testing

```bash
# Test EICAR detection
hex-avg benchmark --test-eicar

# Run benchmarks
hex-avg benchmark
```

### Logs & Reports

```bash
# View recent logs
hex-avg logs --tail

# Generate JSON report
hex-avg report --json --output report.json

# Generate HTML report
hex-avg report --html --output report.html
```

### File Analysis

```bash
# Analyze file
hex-avg analyze /path/to/file

# Deep analysis
hex-avg analyze --deep /path/to/file

# Calculate entropy
hex-avg analyze --entropy /path/to/file
```

---

## 🎯 Example Workflows

### Daily Security Check

```bash
# Update signatures
hex-avg update

# Quick scan of Downloads
hex-avg scan --quick ~/Downloads

# If threats found, quarantine them
hex-avg quarantine list
hex-avg quarantine restore <id>  # if false positive
```

### Full Security Audit

```bash
# Full system scan
hex-avg scan --full --progress

# Generate detailed report
hex-avg report --html --output audit_$(date +%Y%m%d).html

# Review logs
hex-avg logs --tail 100
```

### Malware Analysis

```bash
# Analyze suspicious file
hex-avg analyze --deep suspicious.exe

# Scan with all detection methods
hex-avg scan --heuristic --yara ~/malware_samples

# Generate comprehensive report
hex-avg report --json --output analysis.json
```

---

## 💡 Tips

1. **Start Small**: Begin with scanning small directories
2. **Use Quick Scan**: For routine checks, use quick scan mode
3. **Enable Heuristics**: Heuristic analysis catches unknown threats
4. **Check Logs**: Regularly review logs for suspicious activity
5. **Keep Updated**: Update signatures regularly
6. **Test Safely**: Use EICAR test virus to verify detection

---

## 🆘 Troubleshooting

### Permission Denied (Linux)
```bash
chmod +x hex_avg.py
```

### Python Not Found (Windows)
Add Python to PATH or reinstall with "Add to PATH" checked

### Virtual Environment Issues
```bash
# Linux
rm -rf venv && python3 -m venv venv && source venv/bin/activate

# Windows
Remove-Item -Recurse -Force venv
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Module Import Errors
```bash
# Ensure virtual environment is activated
# Then reinstall dependencies
pip install -r requirements.txt
```

---

## 📚 Next Steps

1. **Read Documentation**:
   - [INSTALLATION.md](docs/INSTALLATION.md) - Detailed installation guide
   - [USAGE.md](docs/USAGE.md) - Complete usage guide
   - [README.md](README.md) - Project overview

2. **Explore Features**:
   - Try different scan types
   - Experiment with detection methods
   - Generate reports
   - Test with EICAR

3. **Learn**:
   - Understand signature-based detection
   - Learn about heuristic analysis
   - Explore YARA rules (Linux)
   - Study the source code

---

## 🎓 Educational Use Cases

### 1. Learn Antivirus Technology
- Understand how antivirus software works
- Study detection methods
- Learn about malware signatures

### 2. Practice Malware Analysis
- Analyze suspicious files safely
- Test detection capabilities
- Practice in a controlled environment

### 3. Defensive Security Training
- Learn defensive security principles
- Practice system scanning
- Understand threat detection

### 4. Cybersecurity Labs
- Set up malware analysis labs
- Create detection rules
- Practice threat hunting

---

## 🔒 Safety Reminders

- ✅ **Use in VMs**: Test in isolated virtual machines
- ✅ **Safe Samples**: Start with EICAR and known safe samples
- ✅ **Backup**: Always backup before scanning important data
- ✅ **Read Only**: HEX-AVG is read-only by default
- ✅ **Educational**: Designed for learning and defensive security

---

## 📞 Get Help

- **Documentation**: See docs/ directory
- **GitHub Issues**: Report bugs and request features
- **Examples**: Check docs/USAGE.md for more examples

---

## 🎉 You're Ready!

You're now ready to use HEX-AVG Antivirus. Start scanning and learning!

**First Command**:
```bash
hex-avg --help
```

**Happy Scanning!** 🔍

---

**HEX-AVG v1.0.0 - Phoenix**  
*Professional Antivirus for Cyber Security Learning*