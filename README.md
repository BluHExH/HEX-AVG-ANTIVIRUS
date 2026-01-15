# 🛡️ HEX-AVG Antivirus v3.0.0

## Professional Cross-Platform Antivirus for Cyber Security Learning &amp; Defensive Security

![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows-lightgrey.svg)

---

## 🎯 What is HEX-AVG?

**HEX-AVG** is a professional, open-source antivirus tool designed specifically for:
- **Cyber security education** and learning
- **Malware analysis laboratories**  
- **Defensive security operations**
- **Kali Linux environments**
- **Windows PowerShell environments**

HEX-AVG v3.0.0 introduces powerful Level-2+ features including advanced heuristic detection, auto-updates, ML-based scoring, cloud signature sync, and a user-friendly GUI.

---

## ✨ Key Features

### 🔍 Advanced Detection Capabilities

#### 1. **Signature-Based Detection** ✅
- Fast hash matching against comprehensive virus database
- EICAR test file support
- Regular signature updates via GitHub Releases
- SQLite database for efficient lookups

#### 2. **Advanced Heuristic Engine** 🆕
- **File Entropy Analysis**: Detects packed/encrypted files (entropy >7.0)
- **File Type vs Extension Mismatch**: Identifies malware disguises
- **Suspicious String Detection**: Finds malicious API calls and patterns
- **Packed/Obfuscated File Detection**: Identifies known packers (UPX, Themida, VMProtect)
- **Combined Scoring System**: All signals combined into 0-100 risk score

**Why This Works:**
- High entropy indicates packed/encrypted content common in malware
- Extension mismatches are a common malware disguise technique
- Suspicious API calls (VirtualAlloc, WriteProcessMemory) indicate malicious behavior
- Packers hide malware from signature detection

#### 3. **YARA Rules Integration** ✅
- Customizable pattern matching for advanced threat hunting
- Pre-built YARA rules for common malware families
- Linux support with libyara

#### 4. **ML-Based Threat Scoring** (Experimental) 🆕
- Offline ML model for malware classification
- Combines with heuristic scores for better accuracy
- **Experimental**: Clearly labeled as such
- Feature-weighted ensemble model
- Privacy-focused: No cloud data required

**Important:** ML scoring is experimental and trained on limited synthetic data. Use alongside signature and heuristic detection.

#### 5. **Cloud Signature Sync** (Optional/Opt-In) 🆕
- Hash-only cloud queries
- **No file uploads** - only hashes sent to cloud
- Offline fallback always available
- User must explicitly opt-in
- Privacy-first design with clear explanations

**Privacy Guarantee:**
- ✅ Only file hashes (MD5, SHA1, SHA256) sent to cloud
- ❌ No file contents, names, or paths
- ❌ No personal information or telemetry
- ✅ Offline mode always available

---

### 🔄 Auto Update System 🆕

**Safe, User-Controlled Updates**

- Check for tool updates: `hex-avg update`
- Update signatures: `hex-avg update --rules`
- GitHub Releases as update source
- User consent **required** before updates
- Safe rollback if update fails
- Offline mode support

**Features:**
- Version checking
- Download and verify packages
- Automatic backup before update
- Restore on failure
- User confirmation prompts

---

### 🖥️ GUI Frontend 🆕

**Cross-Platform User-Friendly Interface**

- **Protection Control**: Start/Stop real-time protection
- **Scanning**: Quick scan, Full scan, Custom folder scan
- **Quarantine Management**: View and manage quarantined files
- **Logs Viewer**: Monitor all HEX-AVG activity
- **Status Dashboard**: Real-time protection and scan status
- **Built with Tkinter**: Works on Windows and Linux

**Launch GUI:**
```bash
hex-avg gui
```

---

### 🛡️ Windows Defender Integration 🆕

**Coexistence Philosophy**

HEX-AVG is designed to **work alongside** Windows Defender, not replace it.

**Multi-Layered Security Approach:**
- **Layer 1**: Windows Defender (Real-time protection, cloud-delivered protection)
- **Layer 2**: HEX-AVG (Signature, heuristic, ML-based detection)

**What HEX-AVG Does:**
- ✅ Detects Defender status
- ✅ Shows friendly coexistence notice
- ✅ Explains multi-layered security benefits
- ✅ NEVER disables Defender
- ✅ Both tools scan independently

**What HEX-AVG Does NOT Do:**
- ❌ Disable Windows Defender
- ❌ Modify Defender settings
- ❌ Interfere with Defender operations

**Benefits of Coexistence:**
- Complementary detection methods
- Defense-in-depth strategy
- Educational insight into different AV engines
- Reduced chance of detection bypass

**Check Status:**
```bash
hex-avg defender
```

---

## 📖 Usage

### Basic Commands

```bash
# Quick scan
hex-avg scan --quick

# Scan specific path
hex-avg scan /path/to/scan

# Full system scan
hex-avg scan --full

# Scan with ML scoring (experimental)
hex-avg scan /path --ml

# Scan with cloud lookup (requires opt-in)
hex-avg scan /path --cloud
```

### Update Management

```bash
# Check for updates
hex-avg update

# Update virus signatures
hex-avg update --rules
```

### GUI Usage

```bash
# Launch GUI
hex-avg gui
```

---

## 📦 Installation

### Windows

```powershell
# Download from GitHub Releases
# Extract and run:
hex-avg.exe scan --quick
```

### Linux

```bash
# Download .deb or AppImage from GitHub Releases

# Debian package:
sudo dpkg -i hex-avg_3.0.0_amd64.deb
hex-avg scan --quick

# AppImage:
chmod +x HEX-AVG-3.0.0-x86_64.AppImage
./HEX-AVG-3.0.0-x86_64.AppImage scan --quick
```

---

## 🔐 Security Model &amp; Limitations

### What HEX-AVG CAN Detect

✅ Known malware via signatures
✅ Unknown malware via heuristics
✅ Packed/obfuscated files
✅ Suspicious behaviors

### What HEX-AVG CANNOT Detect

❌ Kernel-level rootkits (user-space only)
❌ In-memory/fileless malware
❌ Network attacks
❌ Advanced persistence mechanisms

---

## 📚 Documentation

- [BUILD_SYSTEM.md](BUILD_SYSTEM.md) - Build and release documentation
- [INSTALLATION.md](INSTALLATION.md) - Detailed installation guide
- [LEVEL2_ARCHITECTURE.md](LEVEL2_ARCHITECTURE.md) - LEVEL-2 architecture

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

**Version: 3.0.0 | Code Name: Phoenix Rising**  
**Last Updated: 2024**

---

Made with ❤️ by the HEX-AVG Team