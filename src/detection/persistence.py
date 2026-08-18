"""
HEX-AVG Persistence Detection (Windows-focused, experimental)
Detects common persistence mechanisms for educational analysis.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import platform


class PersistenceDetector:
    """Educational detector for common Windows persistence locations."""

    def __init__(self):
        self.is_windows = platform.system().lower() == "windows"

    def analyze(self, target: Optional[Path] = None) -> Dict[str, Any]:
        """
        Analyze common persistence indicators.
        Returns empty/low-risk results on non-Windows or when access is denied.
        """
        result = {
            "platform": platform.system(),
            "checks_run": [],
            "findings": [],
            "risk_score": 0,
        }
        if not self.is_windows:
            result["checks_run"].append("skipped_non_windows")
            return result

        result["checks_run"].append("registry_run_keys")
        try:
            findings = self._check_run_keys()
            result["findings"].extend(findings)
            result["risk_score"] = min(100, len(findings) * 10)
        except Exception as e:
            result["checks_run"].append(f"error:{e}")
        return result

    def _parse_registry_path(self, path: str):
        """Parse registry key path into hive and subkey."""
        import winreg

        if path.startswith("HKLM\\"):
            return winreg.HKEY_LOCAL_MACHINE, path[5:]
        elif path.startswith("HKCU\\"):
            return winreg.HKEY_CURRENT_USER, path[5:]
        else:
            raise ValueError(f"Unknown registry root: {path}")

    def _check_run_keys(self) -> List[Dict[str, Any]]:
        """Check common Run keys for suspicious entries (read-only)."""
        import winreg

        findings: List[Dict[str, Any]] = []
        keys = [
            "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        ]
        for key_path in keys:
            try:
                hive, subkey = self._parse_registry_path(key_path)
                with winreg.OpenKey(hive, subkey) as key:
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            if self._is_suspicious_registry_entry(name, str(value)):
                                findings.append({
                                    "type": "registry_run",
                                    "key": key_path,
                                    "name": name,
                                    "value": str(value)[:200],
                                })
                            i += 1
                        except OSError:
                            break
            except OSError:
                continue
        return findings

    def _is_suspicious_registry_entry(self, name: str, value: str) -> bool:
        """Heuristic check for suspicious Run-key entries."""
        suspicious_extensions = [".exe", ".bat", ".cmd", ".ps1", ".vbs", ".js"]
        suspicious_locations = ["temp", "appdata", "downloads", "public"]
        value_lower = value.lower()
        for ext in suspicious_extensions:
            if ext in value_lower:
                for loc in suspicious_locations:
                    if loc in value_lower:
                        return True
        return False
