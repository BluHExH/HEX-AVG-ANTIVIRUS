"""
Windows Defender Integration and Coexistence
Detects Defender status and shows friendly coexistence notice
"""

import platform
from typing import Dict, List, Optional
import subprocess


class DefenderIntegrator:
    """
    Windows Defender integration and coexistence management
    
    Philosophy:
    - HEX-AVG is designed to coexist with Windows Defender
    - We NEVER disable or modify Windows Defender
    - We provide educational information about multi-layered security
    - Both tools can work together for better protection
    """
    
    def __init__(self):
        self.is_windows = platform.system().lower() == 'windows'
        self.defender_status = None
        self.coexistence_message = """
╔════════════════════════════════════════════════════════════════╗
║           WINDOWS DEFENDER COEXISTENCE NOTICE                 ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  HEX-AVG is designed to WORK ALONGSIDE Windows Defender,     ║
║  not replace it. Multi-layered security is best practice.     ║
║                                                                ║
║  HEX-AVG does NOT disable, weaken, or modify Defender.        ║
║  This notice is informational only.                           ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"""
    
    def check_defender_status(self) -> Dict:
        """Check Windows Defender status (Windows only)."""
        if not self.is_windows:
            return {
                'available': False,
                'reason': 'Not running on Windows',
                'status': 'n/a'
            }
        try:
            # Informational only — read status, never change settings
            result = subprocess.run(
                ['powershell', '-NoProfile', '-Command',
                 'Get-MpComputerStatus | Select-Object -Property AMServiceEnabled,AntispywareEnabled,AntivirusEnabled | ConvertTo-Json'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                return {
                    'available': True,
                    'status': 'detected',
                    'raw': result.stdout.strip()[:500]
                }
            return {'available': True, 'status': 'unknown', 'reason': 'Could not query status'}
        except Exception as e:
            return {'available': False, 'status': 'error', 'reason': str(e)}
    
    def show_coexistence_notice(self) -> None:
        """Print coexistence notice once (Windows only)."""
        if not self.is_windows:
            return
        print(self.coexistence_message)
    
    def get_coexistence_info(self) -> Dict:
        """Return structured coexistence information."""
        status = self.check_defender_status()
        return {
            'defender_status': status.get('status', 'n/a'),
            'coexistence_mode': 'informational',
            'philosophy': 'HEX-AVG never disables or modifies Windows Defender',
            'benefits': [
                'Multi-layered detection approaches',
                'Educational signature/heuristic scanning',
                'No interference with system AV settings'
            ],
            'raw_status': status
        }
    
    def suggest_exclusions(self) -> Optional[List[str]]:
        """
        Suggest optional exclusion paths for advanced users.
        Returns None by default — HEX-AVG does not require exclusions.
        """
        return None
    
    def get_exclusion_instructions(self, paths: List[str]) -> str:
        """Return human-readable exclusion instructions (informational)."""
        if not paths:
            return "No exclusions suggested. HEX-AVG is designed to coexist without them."
        lines = ["Optional exclusion paths (manual, user-controlled):"]
        for p in paths:
            lines.append(f"  - {p}")
        lines.append("Only add exclusions if you fully understand the security implications.")
        return "\n".join(lines)


_defender_instance = None


def get_defender_integrator() -> DefenderIntegrator:
    """Get singleton DefenderIntegrator instance."""
    global _defender_instance
    if _defender_instance is None:
        _defender_instance = DefenderIntegrator()
    return _defender_instance
