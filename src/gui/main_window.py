# File: src/gui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import sys
from pathlib import Path

class ClipboardForensicsGUI:
    def __init__(self, config=None):
        self.config = config or {}
        self.root = tk.Tk()
        self.root.title("Clipboard Forensics Tool v1.0")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        self.setup_ui()
    
    def setup_ui(self):
        # Header
        header = ttk.Frame(self.root, padding="10")
        header.pack(fill=tk.X)
        
        title = ttk.Label(header, text="🔍 Clipboard Forensics Tool", 
                         font=("Arial", 18, "bold"))
        title.pack()
        
        subtitle = ttk.Label(header, text="Cross-Platform Clipboard Analysis", 
                            font=("Arial", 10))
        subtitle.pack()
        
        # Main content
        content = ttk.Frame(self.root, padding="20")
        content.pack(fill=tk.BOTH, expand=True)
        
        # Info section
        info_frame = ttk.LabelFrame(content, text="Analysis Information", padding="10")
        info_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(info_frame, text="Platform: Windows").pack(anchor=tk.W)
        ttk.Label(info_frame, text="Output: output/").pack(anchor=tk.W)
        
        # Controls
        control_frame = ttk.Frame(content)
        control_frame.pack(fill=tk.X, pady=20)
        
        self.analyze_btn = ttk.Button(control_frame, text="▶ Run Analysis", 
                                     command=self.run_analysis, width=20)
        self.analyze_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="📂 Open Output Folder", 
                  command=self.open_output, width=20).pack(side=tk.LEFT, padx=5)
        
        # Log output
        log_frame = ttk.LabelFrame(content, text="Analysis Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, 
                                                  state=tk.DISABLED, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.log("Clipboard Forensics Tool initialized")
        self.log("Click 'Run Analysis' to start extraction")
    
    def log(self, message):
        """Add message to log window"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def run_analysis(self):
        """Run clipboard analysis"""
        self.analyze_btn.config(state=tk.DISABLED)
        self.status.config(text="Running analysis...")
        self.log("\n=== Starting Analysis ===")
        
        try:
            # Run the CLI tool
            result = subprocess.run([
                sys.executable, 'src/main.py', '--cli', 
                '--output', 'output/', '--verbose'
            ], capture_output=True, text=True, timeout=30)
            
            # Display output
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        self.log(line)
            
            if result.returncode == 0:
                self.status.config(text="Analysis complete!")
                self.log("\n✅ Analysis completed successfully!")
                messagebox.showinfo("Success", 
                    "Analysis complete!\nCheck the output/ folder for results.")
            else:
                self.status.config(text="Analysis failed")
                self.log(f"\n❌ Analysis failed: {result.stderr}")
                messagebox.showerror("Error", "Analysis failed. Check log for details.")
                
        except subprocess.TimeoutExpired:
            self.status.config(text="Analysis timed out")
            self.log("\n❌ Analysis timed out after 30 seconds")
            messagebox.showerror("Timeout", "Analysis took too long")
        except Exception as e:
            self.status.config(text=f"Error: {e}")
            self.log(f"\n❌ Error: {e}")
            messagebox.showerror("Error", str(e))
        finally:
            self.analyze_btn.config(state=tk.NORMAL)
    
    def open_output(self):
        """Open output folder"""
        output_path = Path("output").absolute()
        if output_path.exists():
            import os
            os.startfile(output_path)  # Windows
        else:
            messagebox.showwarning("Not Found", "No output folder found. Run analysis first.")
    
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ClipboardForensicsGUI()
    app.run()