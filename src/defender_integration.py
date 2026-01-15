"""
Windows Defender Integration and Coexistence
Detects Defender status and shows friendly coexistence notice
"""

import platform
from typing import Dict, Optional
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
║  not replace it.                                               ║
║                                                                ║
║  🛡️  MULTI-LAYERED SECURITY APPROACH:                        ║
║                                                                ║
║  Layer 1: Windows Defender                                    ║
║  • Real-time protection                                        ║
║  • Cloud-delivered protection                                 ║
║  • Automatic sample submission                                ║
║  • Microsoft's threat intelligence                            ║
║                                                                ║
║  Layer 2: HEX-AVG (Educational/Analysis)                     ║
║  • Signature-based detection                                   ║
║  • Advanced heuristic analysis                                 ║
║  • YARA rule matching                                          ║
║  • Malware analysis capabilities                               ║
║                                                                ║
║  ✅ BOTH TOOLS CAN RUN TOGETHER SAFELY                        ║
║                                                                ║
║  Benefits of coexistence:                                      ║
║  • Complementary detection methods                             ║
║  • Defense-in-depth strategy                                   ║
║  • Educational insight into different AV engines              ║
║  • Reduced chance of detection bypass                          ║
║                                                                ║
║  ⚠️  IMPORTANT:                                               ║
║  • HEX-AVG will NOT disable Windows Defender                  ║
║  • Both tools will scan independently                          ║
║  • Slight performance impact is expected (normal)             ║
║  • This is a feature, not a bug                               ║
║                                                                ║
║  📚 Learn more:                                                ║
║  • Multi-layered security: defense-in-depth                    ║
║  • Why multiple AV tools matter                                ║
║  • Educational cybersecurity                                   ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"""
    
    def check_defender_status(self) -> Dict:
        """
        Check Windows Defender status
        
        Returns:
            Dict with Defender status information
        """
        if not self.is_windows:
            return {
                'enabled': False,
                'status': 'not_applicable',
                'message': 'Windows Defender is only available on Windows',
                'platform': platform.system()
            }
        
        try:
            # Check if Windows Defender is enabled
            # Using PowerShell to query Defender status
            result = subprocess.run(
                ['powershell', '-Command',
                 'Get-MpComputerStatus | Select-Object AntivirusEnabled, '
                 'RealTimeProtectionEnabled, IoavProtectionEnabled | ConvertTo-Json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout:
                import json
                status = json.loads(result.stdout)
                
                is_enabled = status.get('AntivirusEnabled', False) or \
                            status.get('RealTimeProtectionEnabled', False) or \
                            status.get('IoavProtectionEnabled', False)
                
                self.defender_status = {
                    'enabled': is_enabled,
                    'status': 'enabled' if is_enabled else 'disabled',
                    'real_time_enabled': status.get('RealTimeProtectionEnabled', False),
                    'ioav_enabled': status.get('IoavProtectionEnabled', False),
                    'message': 'Windows Defender is active' if is_enabled else 'Windows Defender is disabled'
                }
            else:
                self.defender_status = {
                    'enabled': True,  # Assume enabled if we can't check
                    'status': 'unknown',
                    'message': 'Could not determine Windows Defender status (assuming enabled)'
                }
        
        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            # If we can't check, assume Defender is enabled (safe default)
            self.defender_status = {
                'enabled': True,
                'status': 'unknown',
                'message': f'Could not determine Windows Defender status: {str(e)}'
            }
        
        return self.defender_status
    
    def show_coexistence_notice(self):
        """
        Show coexistence notice to user
        
        This is only shown once per session and provides education
        about multi-layered security.
        """
        if not self.is_windows:
            return
        
        status = self.check_defender_status()
        
        print("="*64)
        print("🛡️  WINDOWS DEFENDER INTEGRATION")
        print("="*64)
        print(f"\nStatus: {status['message']}\n")
        print(self.coexistence_message)
        print("\n" + "="*64)
        print("✅ HEX-AVG will now run alongside Windows Defender")
        print("="*64 + "\n")
    
    def get_coexistence_info(self) -> Dict:
        """
        Get coexistence information
        
        Returns:
            Dict with coexistence details
        """
        status = self.check_defender_status()
        
        return {
            'defender_enabled': status.get('enabled', False),
            'defender_status': status.get('status', 'unknown'),
            'coexistence_mode': 'enabled',
            'philosophy': 'defense_in_depth',
            'benefits': [
                'Complementary detection methods',
                'Multi-layered security approach',
                'Educational cybersecurity learning',
                'Reduced detection bypass risk'
            ],
            'important_notes': [
                'HEX-AVG never disables Windows Defender',
                'Both tools scan independently',
                'Slight performance impact is expected and normal',
                'This is a security feature, not a bug'
            ],
            'performance_impact': 'moderate',
            'recommended_usage': 'run_both'
        }
    
    def is_defender_interfering(self) -> bool:
        """
        Check if Windows Defender is interfering with HEX-AVG
        
        Returns:
            True if interference detected, False otherwise
        """
        if not self.is_windows:
            return False
        
        # Check if HEX-AVG files are being quarantined by Defender
        try:
            result = subprocess.run(
                ['powershell', '-Command',
                 'Get-MpThreatDetection | Where-Object { $_.ThreatName -like "*HEX-AVG*" } | '
                 'Select-Object ThreatName, ActionSuccess | ConvertTo-Json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout:
                import json
                detections = json.loads(result.stdout)
                if detections and isinstance(detections, list) and len(detections) > 0:
                    return True
            
        except:
            pass
        
        return False
    
    def suggest_exclusions(self) -> Optional[List[str]]:
        """
        Suggest Windows Defender exclusions for HEX-AVG
        
        Returns:
            List of paths to exclude, or None if not needed
        """
        if not self.is_windows or not self.is_defender_interfering():
            return None
        
        import os
        
        hex_avg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        return [
            hex_avg_dir,
            os.path.join(hex_avg_dir, 'quarantine'),
            os.path.join(hex_avg_dir, 'signatures'),
            os.path.join(hex_avg_dir, 'logs')
        ]
    
    def get_exclusion_instructions(self, paths: List[str]) -> str:
        """
        Get instructions for adding Windows Defender exclusions
        
        Args:
            paths: List of paths to exclude
            
        Returns:
            Formatted instructions
        """
        instructions = """
╔════════════════════════════════════════════════════════════════╗
║     WINDOWS DEFENDER EXCLUSION INSTRUCTIONS                    ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  If Windows Defender is interfering with HEX-AVG, you can     ║
║  add exclusions to allow HEX-AVG to run normally.             ║
║                                                                ║
║  ⚠️  EXCLUSIONS ARE OPTIONAL - HEX-AVG WILL WORK WITHOUT THEM ║
║                                                                ║
║  To add exclusions via PowerShell (run as Administrator):     ║
║                                                                ║
"""
        
        for path in paths:
            instructions += f'  Add-MpPreference -ExclusionPath "{path}"\n'
        
        instructions += """
║                                                                ║
║  To add exclusions via Windows Security app:                 ║
║  1. Open Windows Security                                     ║
║  2. Go to Virus & threat protection                           ║
║  3. Click "Manage settings"                                   ║
║  4. Scroll to "Exclusions"                                    ║
║  5. Click "Add or remove exclusions"                          ║
║  6. Add the paths listed above                                ║
║                                                                ║
║  To remove exclusions later:                                 ║
║  Remove-MpPreference -ExclusionPath "<path>"                 ║
║                                                                ║
║  📚 Learn more:                                                ║
║  https://docs.microsoft.com/en-us/windows/security/           ║
║  threat-protection/microsoft-defender-antivirus/               ║
║  configure-exclusions-microsoft-defender-antivirus            ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"""
        
        return instructions


# Create global instance
_defender_integrator = None


def get_defender_integrator() -> DefenderIntegrator:
    """Get global defender integrator instance"""
    global _defender_integrator
    if _defender_integrator is None:
        _defender_integrator = DefenderIntegrator()
    return _defender_integrator