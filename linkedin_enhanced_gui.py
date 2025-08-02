#!/usr/bin/env python3
"""
Enhanced LinkedIn Job Application Tool - GUI Version
Features:
- Automatic EasyApply applications
- Lists non-EasyApply jobs for manual application
- Resume-based job matching and filtering
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import queue
import json
import os
from datetime import datetime
from linkedin_enhanced import EnhancedLinkedInAutomation

class EnhancedLinkedInGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced LinkedIn Job Automation Tool")
        self.root.geometry("800x900")
        self.root.resizable(True, True)
        
        # Queue for thread communication
        self.log_queue = queue.Queue()
        
        # Variables
        self.is_running = False
        self.automation = None
        self.resume_path = ""
        
        self.create_widgets()
        self.check_log_queue()
    
    def create_widgets(self):
        """Create and arrange GUI widgets"""
        # Main frame with scrollbar
        main_canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Enhanced LinkedIn Job Automation", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Credentials section
        cred_frame = ttk.LabelFrame(main_frame, text="LinkedIn Credentials", padding="10")
        cred_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(cred_frame, text="Email:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(cred_frame, textvariable=self.email_var, width=50)
        self.email_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(cred_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(cred_frame, textvariable=self.password_var, 
                                       show="*", width=50)
        self.password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Resume section
        resume_frame = ttk.LabelFrame(main_frame, text="Resume Analysis (Optional)", padding="10")
        resume_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(resume_frame, text="Resume File:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        resume_file_frame = ttk.Frame(resume_frame)
        resume_file_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        self.resume_path_var = tk.StringVar()
        self.resume_entry = ttk.Entry(resume_file_frame, textvariable=self.resume_path_var, width=40)
        self.resume_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.browse_button = ttk.Button(resume_file_frame, text="Browse", 
                                       command=self.browse_resume_file)
        self.browse_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Label(resume_frame, text="Min Match Score:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.min_score_var = tk.StringVar(value="0.3")
        self.min_score_entry = ttk.Entry(resume_frame, textvariable=self.min_score_var, width=50)
        self.min_score_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Help text for resume
        help_text = "Supported formats: PDF, DOCX, TXT. Resume analysis enables job matching and filtering."
        help_label = ttk.Label(resume_frame, text=help_text, font=("Arial", 8), foreground="gray")
        help_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Search criteria section
        search_frame = ttk.LabelFrame(main_frame, text="Job Search Criteria", padding="10")
        search_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(search_frame, text="Keywords:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.keywords_var = tk.StringVar()
        self.keywords_entry = ttk.Entry(search_frame, textvariable=self.keywords_var, width=50)
        self.keywords_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(search_frame, text="Location:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.location_var = tk.StringVar()
        self.location_entry = ttk.Entry(search_frame, textvariable=self.location_var, width=50)
        self.location_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(search_frame, text="Max Applications:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.max_apps_var = tk.StringVar(value="50")
        self.max_apps_entry = ttk.Entry(search_frame, textvariable=self.max_apps_var, width=50)
        self.max_apps_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Features section
        features_frame = ttk.LabelFrame(main_frame, text="Automation Features", padding="10")
        features_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.auto_apply_var = tk.BooleanVar(value=True)
        auto_apply_check = ttk.Checkbutton(features_frame, text="Auto-apply to suitable EasyApply jobs", 
                                          variable=self.auto_apply_var)
        auto_apply_check.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.list_manual_var = tk.BooleanVar(value=True)
        list_manual_check = ttk.Checkbutton(features_frame, text="List non-EasyApply jobs for manual application", 
                                           variable=self.list_manual_var)
        list_manual_check.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.resume_filter_var = tk.BooleanVar(value=True)
        resume_filter_check = ttk.Checkbutton(features_frame, text="Filter jobs based on resume match (requires resume)", 
                                             variable=self.resume_filter_var)
        resume_filter_check.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Enhanced Automation", 
                                      command=self.start_automation)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                     command=self.stop_automation, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="Clear Log", 
                                      command=self.clear_log)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        self.open_reports_button = ttk.Button(button_frame, text="Open Reports Folder", 
                                             command=self.open_reports_folder)
        self.open_reports_button.pack(side=tk.LEFT, padx=5)
        
        # Progress section
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_var = tk.StringVar(value="Ready to start enhanced automation...")
        progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Statistics section
        stats_frame = ttk.LabelFrame(main_frame, text="Real-time Statistics", padding="5")
        stats_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        # Statistics labels
        self.stats_labels = {}
        stats_items = [
            ("Total Jobs Found:", "total_jobs"),
            ("EasyApply Jobs:", "easy_apply"),
            ("Non-EasyApply Jobs:", "non_easy_apply"),
            ("Applications Sent:", "applied"),
            ("Suitable Jobs:", "suitable"),
            ("Manual Review Required:", "manual")
        ]
        
        for i, (label_text, key) in enumerate(stats_items):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(stats_grid, text=label_text).grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)
            self.stats_labels[key] = ttk.Label(stats_grid, text="0", font=("Arial", 9, "bold"))
            self.stats_labels[key].grid(row=row, column=col+1, sticky=tk.W, padx=5, pady=2)
        
        # Log display
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="5")
        log_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(8, weight=1)
        cred_frame.columnconfigure(1, weight=1)
        search_frame.columnconfigure(1, weight=1)
        resume_frame.columnconfigure(1, weight=1)
        resume_file_frame.columnconfigure(0, weight=1)
        
        # Pack canvas and scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def browse_resume_file(self):
        """Open file dialog to select resume file"""
        file_types = [
            ("All supported", "*.pdf;*.docx;*.txt"),
            ("PDF files", "*.pdf"),
            ("Word documents", "*.docx"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Resume File",
            filetypes=file_types
        )
        
        if filename:
            self.resume_path_var.set(filename)
            self.resume_path = filename
    
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
        
        try:
            min_score = float(self.min_score_var.get())
            if not 0.0 <= min_score <= 1.0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Min match score must be between 0.0 and 1.0")
            return False
        
        # Check resume file if provided
        resume_path = self.resume_path_var.get().strip()
        if resume_path and not os.path.exists(resume_path):
            messagebox.showerror("Error", f"Resume file not found: {resume_path}")
            return False
        
        return True
    
    def start_automation(self):
        """Start the enhanced automation process"""
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
        self.progress_var.set("Starting enhanced automation...")
        
        # Reset statistics
        for label in self.stats_labels.values():
            label.config(text="0")
        
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
            # Get parameters
            email = self.email_var.get().strip()
            password = self.password_var.get().strip()
            keywords = self.keywords_var.get().strip()
            location = self.location_var.get().strip()
            max_apps = int(self.max_apps_var.get())
            min_score = float(self.min_score_var.get())
            resume_path = self.resume_path_var.get().strip() or None
            
            # Create enhanced automation instance
            automation = EnhancedLinkedInAutomationGUI(
                self.log_queue, 
                self.update_statistics,
                resume_path, 
                min_score
            )
            
            # Run automation
            automation.run_enhanced_automation(email, password, keywords, location, max_apps)
            
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
        self.progress_var.set("Enhanced automation completed")
        
        # Show completion message
        messagebox.showinfo("Complete", 
                           "Enhanced automation finished!\n\n"
                           "Check the reports folder for:\n"
                           "• Comprehensive JSON report\n"
                           "• CSV file with non-EasyApply jobs\n"
                           "• Activity logs")
    
    def update_statistics(self, stats):
        """Update statistics display"""
        def update_ui():
            self.stats_labels["total_jobs"].config(text=str(stats.get("total_jobs", 0)))
            self.stats_labels["easy_apply"].config(text=str(stats.get("easy_apply", 0)))
            self.stats_labels["non_easy_apply"].config(text=str(stats.get("non_easy_apply", 0)))
            self.stats_labels["applied"].config(text=str(stats.get("applied", 0)))
            self.stats_labels["suitable"].config(text=str(stats.get("suitable", 0)))
            self.stats_labels["manual"].config(text=str(stats.get("manual", 0)))
        
        self.root.after(0, update_ui)
    
    def clear_log(self):
        """Clear the log display"""
        self.log_text.delete(1.0, tk.END)
    
    def open_reports_folder(self):
        """Open the reports folder in file explorer"""
        import subprocess
        import sys
        
        try:
            if sys.platform == "win32":
                os.startfile(".")
            elif sys.platform == "darwin":
                subprocess.run(["open", "."])
            else:
                subprocess.run(["xdg-open", "."])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open reports folder: {str(e)}")
    
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

class EnhancedLinkedInAutomationGUI(EnhancedLinkedInAutomation):
    """Extended automation class that logs to GUI and updates statistics"""
    
    def __init__(self, log_queue, stats_callback, resume_path=None, min_match_score=0.3):
        super().__init__(resume_path, min_match_score)
        self.log_queue = log_queue
        self.stats_callback = stats_callback
        
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
    
    def update_gui_statistics(self):
        """Update GUI statistics"""
        stats = {
            "total_jobs": len(self.easy_apply_jobs) + len(self.non_easy_apply_jobs),
            "easy_apply": len(self.easy_apply_jobs),
            "non_easy_apply": len(self.non_easy_apply_jobs),
            "applied": len(self.applied_jobs),
            "suitable": len(self.suitable_jobs),
            "manual": len(self.non_easy_apply_jobs)
        }
        self.stats_callback(stats)
    
    def analyze_and_categorize_jobs(self, jobs):
        """Override to update GUI statistics"""
        result = super().analyze_and_categorize_jobs(jobs)
        self.update_gui_statistics()
        return result
    
    def apply_to_easy_apply_jobs(self, easy_apply_jobs, max_applications=50):
        """Override to update GUI statistics during application process"""
        applications_sent = 0
        
        for job in easy_apply_jobs:
            if applications_sent >= max_applications:
                break
            
            # Skip if resume analysis shows job is not suitable
            if self.resume_data and not job['is_suitable']:
                self.unsuitable_jobs.append(job)
                self.logger.info(f"Skipping unsuitable job: {job['title']} at {job['company']} (Score: {job['match_score']:.2f})")
                self.update_gui_statistics()
                continue
            
            # Apply to the job
            if self.apply_to_job(job):
                applications_sent += 1
                self.suitable_jobs.append(job)
                self.update_gui_statistics()
            
            # Add delay between applications
            time.sleep(3)
        
        self.logger.info(f"Applied to {applications_sent} jobs automatically")

def main():
    """Main function to run the enhanced GUI"""
    root = tk.Tk()
    app = EnhancedLinkedInGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
