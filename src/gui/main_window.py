"""
HEX-AVG GUI Frontend
Cross-platform user-friendly interface using Tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import queue
from pathlib import Path
from typing import Optional
import subprocess
import sys


class HexAvgGUI:
    """
    Main GUI window for HEX-AVG
    
    Features:
    - Start/Stop protection
    - Quick scan, Full scan, Custom scan
    - Logs viewer
    - Quarantine management
    - Status dashboard
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HEX-AVG Antivirus v1.0.0")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Status
        self.is_scanning = False
        self.is_protected = False
        self.scan_queue = queue.Queue()
        
        # Initialize UI
        self._setup_styles()
        self._create_widgets()
        self._load_status()
        
        # Start update loop
        self._update_status()
    
    def _setup_styles(self):
        """Setup UI styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom styles
        style.configure('Header.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Warning.TLabel', foreground='orange')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Info.TLabel', foreground='blue')
        
        style.configure('Primary.TButton', font=('Arial', 10, 'bold'))
        style.configure('Danger.TButton', foreground='red')
        
    def _create_widgets(self):
        """Create main UI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame,
            text="🛡️  HEX-AVG Antivirus",
            style='Header.TLabel'
        )
        title_label.pack(side=tk.LEFT)
        
        version_label = ttk.Label(header_frame, text="v1.0.0 | Phoenix")
        version_label.pack(side=tk.RIGHT)
        
        # Left Panel - Controls
        left_panel = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Protection Controls
        protection_frame = ttk.LabelFrame(left_panel, text="Protection", padding="5")
        protection_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.protection_btn = ttk.Button(
            protection_frame,
            text="▶ Start Protection",
            command=self._toggle_protection,
            style='Primary.TButton'
        )
        self.protection_btn.pack(fill=tk.X, pady=5)
        
        self.protection_status = ttk.Label(
            protection_frame,
            text="Protection: OFF",
            style='Error.TLabel'
        )
        self.protection_status.pack()
        
        # Scan Controls
        scan_frame = ttk.LabelFrame(left_panel, text="Scan", padding="5")
        scan_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            scan_frame,
            text="⚡ Quick Scan",
            command=self._quick_scan
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            scan_frame,
            text="🔍 Full Scan",
            command=self._full_scan
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            scan_frame,
            text="📁 Custom Scan",
            command=self._custom_scan
        ).pack(fill=tk.X, pady=2)
        
        # Update Controls
        update_frame = ttk.LabelFrame(left_panel, text="Updates", padding="5")
        update_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            update_frame,
            text="🔄 Check for Updates",
            command=self._check_updates
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            update_frame,
            text="📥 Update Signatures",
            command=self._update_signatures
        ).pack(fill=tk.X, pady=2)
        
        # Quarantine Controls
        quarantine_frame = ttk.LabelFrame(left_panel, text="Quarantine", padding="5")
        quarantine_frame.pack(fill=tk.X)
        
        ttk.Button(
            quarantine_frame,
            text="📋 View Quarantine",
            command=self._view_quarantine
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            quarantine_frame,
            text="🗑️ Clear Quarantine",
            command=self._clear_quarantine
        ).pack(fill=tk.X, pady=2)
        
        # Right Panel - Status & Logs
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status Dashboard
        status_frame = ttk.LabelFrame(right_panel, text="Status Dashboard", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Status indicators
        self.scan_status_label = ttk.Label(status_frame, text="Scan Status: Idle")
        self.scan_status_label.pack(anchor=tk.W)
        
        self.files_scanned_label = ttk.Label(status_frame, text="Files Scanned: 0")
        self.files_scanned_label.pack(anchor=tk.W)
        
        self.threats_found_label = ttk.Label(status_frame, text="Threats Found: 0", style='Success.TLabel')
        self.threats_found_label.pack(anchor=tk.W)
        
        self.scan_progress = ttk.Progressbar(
            status_frame,
            mode='indeterminate',
            length=300
        )
        self.scan_progress.pack(fill=tk.X, pady=(10, 0))
        
        # Logs Viewer
        logs_frame = ttk.LabelFrame(right_panel, text="Activity Log", padding="10")
        logs_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            logs_frame,
            height=20,
            width=80,
            wrap=tk.WORD,
            font=('Consolas', 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
        # Bottom Panel - Info
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        info_label = ttk.Label(
            bottom_frame,
            text="HEX-AVG is designed for cybersecurity education and defensive security operations. "
                 "This is an open-source project.",
            style='Info.TLabel'
        )
        info_label.pack(side=tk.LEFT)
        
        # Menu Bar
        self._create_menu()
    
    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Scan Folder...", command=self._custom_scan)
        file_menu.add_command(label="View Quarantine", command=self._view_quarantine)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Quick Scan", command=self._quick_scan)
        tools_menu.add_command(label="Full Scan", command=self._full_scan)
        tools_menu.add_separator()
        tools_menu.add_command(label="Update Signatures", command=self._update_signatures)
        tools_menu.add_command(label="Check for Updates", command=self._check_updates)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Documentation", command=self._show_documentation)
    
    def _log(self, message: str, level: str = "INFO"):
        """Add message to log"""
        timestamp = tk.datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] [{level}] {message}\n")
        self.log_text.see(tk.END)
    
    def _load_status(self):
        """Load current status"""
        self._log("HEX-AVG GUI initialized", "INFO")
        self._log("Protection is currently OFF", "WARNING")
    
    def _toggle_protection(self):
        """Toggle protection on/off"""
        if self.is_protected:
            self.is_protected = False
            self.protection_btn.config(text="▶ Start Protection")
            self.protection_status.config(text="Protection: OFF", style='Error.TLabel')
            self._log("Protection stopped", "WARNING")
        else:
            self.is_protected = True
            self.protection_btn.config(text="⏸ Stop Protection")
            self.protection_status.config(text="Protection: ON", style='Success.TLabel')
            self._log("Protection started", "INFO")
    
    def _quick_scan(self):
        """Start quick scan"""
        if self.is_scanning:
            messagebox.showwarning("Scan in Progress", "A scan is already running!")
            return
        
        self._start_scan("--quick")
    
    def _full_scan(self):
        """Start full scan"""
        if self.is_scanning:
            messagebox.showwarning("Scan in Progress", "A scan is already running!")
            return
        
        self._start_scan("/")
    
    def _custom_scan(self):
        """Start custom scan"""
        if self.is_scanning:
            messagebox.showwarning("Scan in Progress", "A scan is already running!")
            return
        
        folder = filedialog.askdirectory(title="Select Folder to Scan")
        if folder:
            self._start_scan(folder)
    
    def _start_scan(self, path: str):
        """Start scan in background thread"""
        self.is_scanning = True
        self.scan_status_label.config(text="Scan Status: Running")
        self.scan_progress.start(10)
        self._log(f"Starting scan: {path}", "INFO")
        
        # Run scan in background thread
        thread = threading.Thread(target=self._run_scan, args=(path,))
        thread.daemon = True
        thread.start()
    
    def _run_scan(self, path: str):
        """Run scan command in background"""
        try:
            # Execute CLI scan
            result = subprocess.run(
                [sys.executable, "hex_avg.py", "scan", path],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            # Parse output and update UI
            output = result.stdout + result.stderr
            
            # Update log with scan output
            for line in output.split('\n')[:50]:  # Limit to 50 lines
                if line.strip():
                    self.root.after(0, lambda l=line: self._log(l))
            
            self.root.after(0, self._scan_complete)
            
        except subprocess.TimeoutExpired:
            self.root.after(0, lambda: self._log("Scan timed out", "ERROR"))
            self.root.after(0, self._scan_complete)
        except Exception as e:
            self.root.after(0, lambda: self._log(f"Scan error: {str(e)}", "ERROR"))
            self.root.after(0, self._scan_complete)
    
    def _scan_complete(self):
        """Handle scan completion"""
        self.is_scanning = False
        self.scan_status_label.config(text="Scan Status: Complete")
        self.scan_progress.stop()
        self._log("Scan completed", "INFO")
        
        messagebox.showinfo("Scan Complete", "The scan has finished. Check the activity log for details.")
    
    def _check_updates(self):
        """Check for updates"""
        self._log("Checking for updates...", "INFO")
        messagebox.showinfo("Updates", "This feature requires the update_manager module. Please use CLI: hex-avg update")
    
    def _update_signatures(self):
        """Update virus signatures"""
        self._log("Updating virus signatures...", "INFO")
        messagebox.showinfo("Signatures", "This feature requires the update_manager module. Please use CLI: hex-avg update --rules")
    
    def _view_quarantine(self):
        """View quarantine"""
        self._log("Opening quarantine...", "INFO")
        messagebox.showinfo("Quarantine", "This feature requires quarantine management module. Please use CLI: hex-avg quarantine list")
    
    def _clear_quarantine(self):
        """Clear quarantine"""
        if messagebox.askyesno("Clear Quarantine", "Are you sure you want to clear all quarantined files?"):
            self._log("Clearing quarantine...", "WARNING")
            messagebox.showinfo("Quarantine", "This feature requires quarantine management module. Please use CLI: hex-avg quarantine clear")
    
    def _show_about(self):
        """Show about dialog"""
        about_text = """HEX-AVG Antivirus v1.0.0
Phoenix Edition

A professional, open-source antivirus tool designed for:
• Cybersecurity education
• Malware analysis laboratories
• Defensive security operations

Developed by the HEX-AVG Team
License: MIT

For more information, visit:
https://github.com/yourusername/hex-avg"""
        
        messagebox.showinfo("About HEX-AVG", about_text)
    
    def _show_documentation(self):
        """Show documentation"""
        messagebox.showinfo("Documentation", "Full documentation is available at:\nhttps://github.com/yourusername/hex-avg/blob/main/README.md")
    
    def _update_status(self):
        """Update status periodically"""
        # This would check actual status from CLI
        # For now, just schedule next update
        self.root.after(5000, self._update_status)
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()


def launch_gui():
    """Launch HEX-AVG GUI"""
    app = HexAvgGUI()
    app.run()


if __name__ == "__main__":
    launch_gui()