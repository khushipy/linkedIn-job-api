#!/usr/bin/env python3
"""
LinkedIn EasyApply Automation Tool - GUI Version
Simple GUI interface for the LinkedIn automation tool
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import queue
import json
from linkedin_easyapply import LinkedInEasyApply

class LinkedInGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn EasyApply Automation Tool")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # Queue for thread communication
        self.log_queue = queue.Queue()
        
        # Variables
        self.is_running = False
        self.automation = None
        
        self.create_widgets()
        self.check_log_queue()
    
    def create_widgets(self):
        """Create and arrange GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="LinkedIn EasyApply Automation", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Credentials section
        cred_frame = ttk.LabelFrame(main_frame, text="LinkedIn Credentials", padding="10")
        cred_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(cred_frame, text="Email:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(cred_frame, textvariable=self.email_var, width=40)
        self.email_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(cred_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(cred_frame, textvariable=self.password_var, 
                                       show="*", width=40)
        self.password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Search criteria section
        search_frame = ttk.LabelFrame(main_frame, text="Job Search Criteria", padding="10")
        search_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(search_frame, text="Keywords:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.keywords_var = tk.StringVar()
        self.keywords_entry = ttk.Entry(search_frame, textvariable=self.keywords_var, width=40)
        self.keywords_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(search_frame, text="Location:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.location_var = tk.StringVar()
        self.location_entry = ttk.Entry(search_frame, textvariable=self.location_var, width=40)
        self.location_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(search_frame, text="Max Applications:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.max_apps_var = tk.StringVar(value="50")
        self.max_apps_entry = ttk.Entry(search_frame, textvariable=self.max_apps_var, width=40)
        self.max_apps_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Automation", 
                                      command=self.start_automation)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                     command=self.stop_automation, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="Clear Log", 
                                      command=self.clear_log)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Ready to start...")
        progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        progress_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Log display
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="5")
        log_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=70)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        cred_frame.columnconfigure(1, weight=1)
        search_frame.columnconfigure(1, weight=1)
    
    def validate_inputs(self):
        """Validate user inputs"""
        if not self.email_var.get().strip():
            messagebox.showerror("Error", "Please enter your LinkedIn email")
            return False
        
        if not self.password_var.get().strip():
            messagebox.showerror("Error", "Please enter your LinkedIn password")
            return False
        
        try:
            max_apps = int(self.max_apps_var.get())
            if max_apps <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Max applications must be a positive number")
            return False
        
        return True
    
    def start_automation(self):
        """Start the automation process"""
        if not self.validate_inputs():
            return
        
        if self.is_running:
            messagebox.showwarning("Warning", "Automation is already running")
            return
        
        # Update UI state
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_bar.start()
        self.progress_var.set("Starting automation...")
        
        # Clear previous log
        self.log_text.delete(1.0, tk.END)
        
        # Start automation in separate thread
        automation_thread = threading.Thread(target=self.run_automation_thread)
        automation_thread.daemon = True
        automation_thread.start()
    
    def stop_automation(self):
        """Stop the automation process"""
        self.is_running = False
        self.progress_var.set("Stopping...")
        self.log_message("Stopping automation...")
    
    def run_automation_thread(self):
        """Run automation in separate thread"""
        try:
            # Create custom automation class that logs to GUI
            automation = LinkedInEasyApplyGUI(self.log_queue)
            
            # Get parameters
            email = self.email_var.get().strip()
            password = self.password_var.get().strip()
            keywords = self.keywords_var.get().strip()
            location = self.location_var.get().strip()
            max_apps = int(self.max_apps_var.get())
            
            # Run automation
            automation.run_automation(email, password, keywords, location, max_apps)
            
        except Exception as e:
            self.log_queue.put(f"ERROR: {str(e)}")
        finally:
            # Update UI state
            self.root.after(0, self.automation_finished)
    
    def automation_finished(self):
        """Called when automation finishes"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_bar.stop()
        self.progress_var.set("Automation completed")
        
        # Show completion message
        messagebox.showinfo("Complete", "Automation finished! Check the log for details.")
    
    def clear_log(self):
        """Clear the log display"""
        self.log_text.delete(1.0, tk.END)
    
    def log_message(self, message):
        """Add message to log display"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
    
    def check_log_queue(self):
        """Check for new log messages from automation thread"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_message(message)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_log_queue)

class LinkedInEasyApplyGUI(LinkedInEasyApply):
    """Extended automation class that logs to GUI"""
    
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue
        
        # Override logger to send to GUI
        import logging
        
        class GUIHandler(logging.Handler):
            def __init__(self, queue):
                super().__init__()
                self.queue = queue
            
            def emit(self, record):
                msg = self.format(record)
                self.queue.put(msg)
        
        # Add GUI handler to logger
        gui_handler = GUIHandler(self.log_queue)
        gui_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        self.logger.addHandler(gui_handler)

def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = LinkedInGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
