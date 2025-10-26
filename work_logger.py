#!/usr/bin/env python3
"""
Work Logger - Track your hourly work tasks
A desktop app that reminds you every hour to document what you've been working on.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import sys
from datetime import datetime, timedelta
from threading import Thread, Event
import time

# Version information
VERSION = "1.0.0"

# Import updater module
try:
    from updater import Updater
    UPDATER_AVAILABLE = True
except ImportError:
    UPDATER_AVAILABLE = False


class Task:
    """Represents a work task with start time, description, and completion status."""

    def __init__(self, description, start_time=None, end_time=None, completed=False):
        self.description = description
        self.start_time = start_time or datetime.now().isoformat()
        self.end_time = end_time
        self.completed = completed

    def complete(self):
        """Mark task as completed and record end time."""
        self.completed = True
        self.end_time = datetime.now().isoformat()

    def to_dict(self):
        """Convert task to dictionary for JSON serialization."""
        return {
            'description': self.description,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'completed': self.completed
        }

    @classmethod
    def from_dict(cls, data):
        """Create task from dictionary."""
        return cls(
            description=data['description'],
            start_time=data['start_time'],
            end_time=data.get('end_time'),
            completed=data.get('completed', False)
        )

    def duration_str(self):
        """Get human-readable duration string."""
        if not self.end_time:
            return "In progress"

        start = datetime.fromisoformat(self.start_time)
        end = datetime.fromisoformat(self.end_time)
        duration = end - start

        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"


class WorkLogger:
    """Main application class for Work Logger."""

    LOGS_DIR = 'logs'

    def __init__(self, root):
        self.root = root
        self.root.title(f"Work Logger v{VERSION}")
        self.root.geometry("700x600")

        self.tasks = []
        self.current_task = None
        self.reminder_interval = 60 * 60  # 60 minutes in seconds (configurable)
        self.reminder_thread = None
        self.stop_reminder = Event()

        # Create logs directory if it doesn't exist
        if not os.path.exists(self.LOGS_DIR):
            os.makedirs(self.LOGS_DIR)

        # Migrate old data format if needed
        self.migrate_old_data()

        self.load_tasks()
        self.setup_ui()
        self.start_reminder_timer()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        """Create the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Current Task Section
        current_frame = ttk.LabelFrame(main_frame, text="Current Task", padding="10")
        current_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        current_frame.columnconfigure(0, weight=1)

        self.current_task_label = ttk.Label(
            current_frame,
            text="No active task",
            font=("Arial", 12, "bold"),
            foreground="gray"
        )
        self.current_task_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.current_task_time = ttk.Label(current_frame, text="", foreground="blue")
        self.current_task_time.grid(row=1, column=0, sticky=tk.W)

        # New Task Section
        new_task_frame = ttk.LabelFrame(main_frame, text="New Task", padding="10")
        new_task_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        new_task_frame.columnconfigure(0, weight=1)

        ttk.Label(new_task_frame, text="What are you working on?").grid(row=0, column=0, sticky=tk.W)

        self.task_entry = ttk.Entry(new_task_frame, width=50)
        self.task_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 10))
        self.task_entry.bind('<Return>', lambda e: self.start_new_task())

        button_frame = ttk.Frame(new_task_frame)
        button_frame.grid(row=2, column=0, sticky=tk.W)

        self.start_btn = ttk.Button(
            button_frame,
            text="Start New Task",
            command=self.start_new_task
        )
        self.start_btn.grid(row=0, column=0, padx=(0, 5))

        self.finish_btn = ttk.Button(
            button_frame,
            text="Finish Current & Start New",
            command=self.finish_and_start_new,
            state=tk.DISABLED
        )
        self.finish_btn.grid(row=0, column=1)

        # Task History Section
        history_frame = ttk.LabelFrame(main_frame, text="Task History", padding="10")
        history_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Scrolled text for task history
        self.history_text = scrolledtext.ScrolledText(
            history_frame,
            width=60,
            height=15,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.history_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Buttons for task management
        history_btn_frame = ttk.Frame(history_frame)
        history_btn_frame.grid(row=1, column=0, sticky=tk.W)

        ttk.Button(
            history_btn_frame,
            text="Edit Selected Task",
            command=self.edit_task
        ).grid(row=0, column=0, padx=(0, 5))

        ttk.Button(
            history_btn_frame,
            text="Delete Selected Task",
            command=self.delete_task
        ).grid(row=0, column=1, padx=(0, 5))

        # Enable text selection
        self.history_text.bind("<Button-1>", self.on_history_click)
        self.selected_task_index = None

        # Settings Section
        settings_frame = ttk.Frame(main_frame)
        settings_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Label(settings_frame, text="Reminder Interval (minutes):").grid(row=0, column=0, sticky=tk.W)

        self.interval_var = tk.StringVar(value="60")
        interval_spinbox = ttk.Spinbox(
            settings_frame,
            from_=1,
            to=240,
            textvariable=self.interval_var,
            width=10,
            command=self.update_reminder_interval
        )
        interval_spinbox.grid(row=0, column=1, padx=(5, 10))

        ttk.Button(
            settings_frame,
            text="Update Interval",
            command=self.update_reminder_interval
        ).grid(row=0, column=2)

        ttk.Button(
            settings_frame,
            text="Test Reminder Now",
            command=self.show_reminder
        ).grid(row=0, column=3, padx=(10, 0))

        # Add Update button if updater is available
        if UPDATER_AVAILABLE:
            ttk.Button(
                settings_frame,
                text="Check for Updates",
                command=self.check_for_updates
            ).grid(row=0, column=4, padx=(10, 0))

        # Update UI
        self.update_ui()

    def start_new_task(self):
        """Start a new task."""
        description = self.task_entry.get().strip()

        if not description:
            messagebox.showwarning("Empty Task", "Please enter a task description.")
            return

        # If there's a current task, ask to finish it
        if self.current_task and not self.current_task.completed:
            response = messagebox.askyesno(
                "Current Task Active",
                "You have an active task. Do you want to finish it first?"
            )
            if response:
                self.current_task.complete()

        # Create new task
        new_task = Task(description)
        self.tasks.append(new_task)
        self.current_task = new_task

        # Clear entry
        self.task_entry.delete(0, tk.END)

        # Save and update UI
        self.save_tasks()
        self.update_ui()

    def finish_and_start_new(self):
        """Finish current task and start a new one."""
        if self.current_task and not self.current_task.completed:
            self.current_task.complete()
            self.save_tasks()

        self.start_new_task()

    def update_ui(self):
        """Update the user interface with current task and history."""
        # Update current task display
        if self.current_task and not self.current_task.completed:
            self.current_task_label.config(
                text=self.current_task.description,
                foreground="green"
            )
            start_time = datetime.fromisoformat(self.current_task.start_time)
            self.current_task_time.config(
                text=f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            self.finish_btn.config(state=tk.NORMAL)
        else:
            self.current_task_label.config(
                text="No active task",
                foreground="gray"
            )
            self.current_task_time.config(text="")
            self.finish_btn.config(state=tk.DISABLED)

        # Update task history
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)

        # Store task line mapping for selection
        self.task_line_map = {}

        if not self.tasks:
            self.history_text.insert(tk.END, "No tasks logged yet.")
        else:
            for i, task in enumerate(reversed(self.tasks), 1):
                # Store the line number for this task
                line_start = self.history_text.index(tk.INSERT)
                actual_index = len(self.tasks) - i  # Index in self.tasks list
                self.task_line_map[int(line_start.split('.')[0])] = actual_index

                start = datetime.fromisoformat(task.start_time)
                status = "✓ Completed" if task.completed else "⏱ In Progress"

                self.history_text.insert(tk.END, f"{i}. {task.description}\n", "task_name")
                self.history_text.insert(
                    tk.END,
                    f"   Started: {start.strftime('%Y-%m-%d %H:%M')}\n"
                )

                if task.completed:
                    end = datetime.fromisoformat(task.end_time)
                    self.history_text.insert(
                        tk.END,
                        f"   Ended: {end.strftime('%Y-%m-%d %H:%M')}\n"
                    )
                    self.history_text.insert(
                        tk.END,
                        f"   Duration: {task.duration_str()}\n"
                    )

                self.history_text.insert(tk.END, f"   Status: {status}\n\n")

        self.history_text.config(state=tk.DISABLED)

    def on_history_click(self, event):
        """Handle clicks in history text to select tasks."""
        # Get the line number that was clicked
        index = self.history_text.index(f"@{event.x},{event.y}")
        line_num = int(index.split('.')[0])

        # Find which task this line belongs to
        for task_line, task_index in self.task_line_map.items():
            # Check if click is within task's lines (each task takes about 5-6 lines)
            if task_line <= line_num < task_line + 6:
                self.selected_task_index = task_index
                # Highlight the selection
                self.highlight_selected_task(task_line)
                return

    def highlight_selected_task(self, start_line):
        """Highlight the selected task in the history."""
        self.history_text.tag_remove("highlight", "1.0", tk.END)
        self.history_text.tag_add("highlight", f"{start_line}.0", f"{start_line + 6}.0")
        self.history_text.tag_config("highlight", background="lightblue")

    def edit_task(self):
        """Edit the selected task."""
        if self.selected_task_index is None:
            messagebox.showwarning("No Selection", "Please click on a task to select it first.")
            return

        task = self.tasks[self.selected_task_index]

        # Create edit dialog
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Task")
        edit_window.geometry("500x300")

        frame = ttk.Frame(edit_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # Task description
        ttk.Label(frame, text="Task Description:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        desc_text = scrolledtext.ScrolledText(frame, height=5, wrap=tk.WORD)
        desc_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        desc_text.insert(tk.END, task.description)

        # Start time
        ttk.Label(frame, text="Start Time:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        start_var = tk.StringVar(value=task.start_time)
        start_entry = ttk.Entry(frame, textvariable=start_var, width=40)
        start_entry.pack(anchor=tk.W, pady=(0, 10))

        # End time (if completed)
        if task.completed:
            ttk.Label(frame, text="End Time:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
            end_var = tk.StringVar(value=task.end_time or "")
            end_entry = ttk.Entry(frame, textvariable=end_var, width=40)
            end_entry.pack(anchor=tk.W, pady=(0, 10))

        def save_changes():
            new_desc = desc_text.get("1.0", tk.END).strip()
            if not new_desc:
                messagebox.showwarning("Empty Description", "Task description cannot be empty.")
                return

            # Validate timestamps
            try:
                datetime.fromisoformat(start_var.get())
                if task.completed and end_var.get():
                    datetime.fromisoformat(end_var.get())
            except ValueError:
                messagebox.showerror("Invalid Time", "Invalid timestamp format. Use ISO format: YYYY-MM-DD HH:MM:SS")
                return

            # Update task
            task.description = new_desc
            task.start_time = start_var.get()
            if task.completed and end_var.get():
                task.end_time = end_var.get()

            self.save_tasks()
            self.update_ui()
            edit_window.destroy()
            messagebox.showinfo("Success", "Task updated successfully!")

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=(10, 0))

        ttk.Button(btn_frame, text="Save Changes", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)

    def delete_task(self):
        """Delete the selected task."""
        if self.selected_task_index is None:
            messagebox.showwarning("No Selection", "Please click on a task to select it first.")
            return

        task = self.tasks[self.selected_task_index]

        # Confirm deletion
        response = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete this task?\n\n\"{task.description}\""
        )

        if response:
            # Check if it's the current task
            if task == self.current_task:
                self.current_task = None

            # Remove task from list
            self.tasks.pop(self.selected_task_index)
            self.selected_task_index = None

            self.save_tasks()
            self.update_ui()
            messagebox.showinfo("Success", "Task deleted successfully!")

    def get_log_file_path(self, date):
        """Get the log file path for a specific date."""
        date_str = date.strftime('%Y-%m-%d')
        return os.path.join(self.LOGS_DIR, f"{date_str}.json")

    def save_tasks(self):
        """Save tasks to daily JSON files."""
        # Group tasks by date
        tasks_by_date = {}
        for task in self.tasks:
            task_date = datetime.fromisoformat(task.start_time).date()
            date_str = task_date.strftime('%Y-%m-%d')
            if date_str not in tasks_by_date:
                tasks_by_date[date_str] = []
            tasks_by_date[date_str].append(task)

        # Save each day's tasks to its own file
        for date_str, day_tasks in tasks_by_date.items():
            file_path = os.path.join(self.LOGS_DIR, f"{date_str}.json")
            data = {
                'date': date_str,
                'tasks': [task.to_dict() for task in day_tasks]
            }
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)

        # Save current task reference separately
        current_task_file = os.path.join(self.LOGS_DIR, 'current_task.json')
        current_data = {
            'current_task': self.current_task.to_dict() if self.current_task and not self.current_task.completed else None
        }
        with open(current_task_file, 'w') as f:
            json.dump(current_data, f, indent=2)

    def migrate_old_data(self):
        """Migrate data from old work_log.json format to new daily files format."""
        OLD_DATA_FILE = 'work_log.json'

        if os.path.exists(OLD_DATA_FILE):
            try:
                print("Migrating old data format to daily log files...")
                with open(OLD_DATA_FILE, 'r') as f:
                    data = json.load(f)

                tasks = [Task.from_dict(task_data) for task_data in data.get('tasks', [])]

                if tasks:
                    # Group tasks by date and save to daily files
                    tasks_by_date = {}
                    for task in tasks:
                        task_date = datetime.fromisoformat(task.start_time).date()
                        date_str = task_date.strftime('%Y-%m-%d')
                        if date_str not in tasks_by_date:
                            tasks_by_date[date_str] = []
                        tasks_by_date[date_str].append(task)

                    # Save to daily files
                    for date_str, day_tasks in tasks_by_date.items():
                        file_path = os.path.join(self.LOGS_DIR, f"{date_str}.json")
                        file_data = {
                            'date': date_str,
                            'tasks': [task.to_dict() for task in day_tasks]
                        }
                        with open(file_path, 'w') as f:
                            json.dump(file_data, f, indent=2)

                    # Handle current task
                    current_index = data.get('current_task_index')
                    if current_index is not None and 0 <= current_index < len(tasks):
                        current_task = tasks[current_index]
                        if not current_task.completed:
                            current_task_file = os.path.join(self.LOGS_DIR, 'current_task.json')
                            current_data = {'current_task': current_task.to_dict()}
                            with open(current_task_file, 'w') as f:
                                json.dump(current_data, f, indent=2)

                # Rename old file to backup
                backup_file = 'work_log.json.backup'
                os.rename(OLD_DATA_FILE, backup_file)
                print(f"Migration complete! Old file backed up to {backup_file}")

            except Exception as e:
                print(f"Error during migration: {e}")

    def load_tasks(self):
        """Load tasks from all daily JSON files."""
        self.tasks = []

        # Load all log files from the logs directory
        if os.path.exists(self.LOGS_DIR):
            try:
                log_files = sorted([f for f in os.listdir(self.LOGS_DIR) if f.endswith('.json') and f != 'current_task.json'])

                for log_file in log_files:
                    file_path = os.path.join(self.LOGS_DIR, log_file)
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            tasks = [Task.from_dict(task_data) for task_data in data.get('tasks', [])]
                            self.tasks.extend(tasks)
                    except Exception as e:
                        print(f"Error loading {log_file}: {e}")

                # Sort tasks by start time
                self.tasks.sort(key=lambda t: t.start_time)

                # Load current task reference
                current_task_file = os.path.join(self.LOGS_DIR, 'current_task.json')
                if os.path.exists(current_task_file):
                    with open(current_task_file, 'r') as f:
                        current_data = json.load(f)
                        current_task_dict = current_data.get('current_task')
                        if current_task_dict:
                            # Find the current task in the loaded tasks
                            for task in self.tasks:
                                if (task.start_time == current_task_dict['start_time'] and
                                    task.description == current_task_dict['description']):
                                    if not task.completed:
                                        self.current_task = task
                                    break

            except Exception as e:
                messagebox.showerror("Load Error", f"Error loading tasks: {e}")

    def start_reminder_timer(self):
        """Start background thread for hourly reminders."""
        self.stop_reminder.clear()
        self.reminder_thread = Thread(target=self._reminder_loop, daemon=True)
        self.reminder_thread.start()

    def _reminder_loop(self):
        """Background loop that shows reminders at intervals."""
        while not self.stop_reminder.is_set():
            # Wait for the interval (checking every second for stop signal)
            for _ in range(self.reminder_interval):
                if self.stop_reminder.is_set():
                    return
                time.sleep(1)

            # Show reminder
            self.root.after(0, self.show_reminder)

    def show_reminder(self):
        """Show reminder popup to log work."""
        reminder_window = tk.Toplevel(self.root)
        reminder_window.title("Work Logger Reminder")
        reminder_window.geometry("400x250")

        # Make window appear on top
        reminder_window.attributes('-topmost', True)
        reminder_window.lift()
        reminder_window.focus_force()

        # Flash the window to get attention
        self._flash_window(reminder_window)

        frame = ttk.Frame(reminder_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # Message
        ttk.Label(
            frame,
            text="⏰ Time to log your work!",
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 10))

        ttk.Label(
            frame,
            text="What have you been working on?",
            font=("Arial", 10)
        ).pack(pady=(0, 10))

        # Entry for quick task log
        task_var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=task_var, width=40)
        entry.pack(pady=(0, 20))
        entry.focus()

        def log_task():
            description = task_var.get().strip()
            if description:
                # Finish current task if any
                if self.current_task and not self.current_task.completed:
                    self.current_task.complete()

                # Create new task
                new_task = Task(description)
                self.tasks.append(new_task)
                self.current_task = new_task

                self.save_tasks()
                self.update_ui()

            reminder_window.destroy()

        def open_main():
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            reminder_window.destroy()

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack()

        ttk.Button(btn_frame, text="Log Task", command=log_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Open Main Window", command=open_main).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remind Me Later", command=reminder_window.destroy).pack(side=tk.LEFT, padx=5)

        entry.bind('<Return>', lambda e: log_task())

    def _flash_window(self, window, times=3):
        """Flash window to get user's attention."""
        original_color = window.cget('bg')

        def flash(count):
            if count > 0:
                current_color = window.cget('bg')
                new_color = 'yellow' if current_color == original_color else original_color
                window.configure(bg=new_color)
                window.after(200, lambda: flash(count - 1))

        flash(times * 2)

    def update_reminder_interval(self):
        """Update the reminder interval from user input."""
        try:
            minutes = int(self.interval_var.get())
            if minutes < 1:
                raise ValueError("Interval must be at least 1 minute")

            self.reminder_interval = minutes * 60

            # Restart reminder timer with new interval
            self.stop_reminder.set()
            if self.reminder_thread:
                self.reminder_thread.join(timeout=2)
            self.start_reminder_timer()

            messagebox.showinfo(
                "Interval Updated",
                f"Reminder interval set to {minutes} minute(s)."
            )
        except ValueError as e:
            messagebox.showerror("Invalid Interval", str(e))

    def check_for_updates(self):
        """Check for application updates from GitHub."""
        if not UPDATER_AVAILABLE:
            messagebox.showerror("Update Error", "Updater module is not available.")
            return

        # Create progress window
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Checking for Updates")
        progress_window.geometry("400x200")
        progress_window.transient(self.root)
        progress_window.grab_set()

        frame = ttk.Frame(progress_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        status_label = ttk.Label(frame, text="Checking for updates...", font=("Arial", 10))
        status_label.pack(pady=(0, 20))

        progress_bar = ttk.Progressbar(frame, mode='indeterminate', length=300)
        progress_bar.pack(pady=(0, 20))
        progress_bar.start()

        def check_updates_thread():
            """Background thread to check for updates."""
            try:
                updater = Updater(VERSION)
                is_available, latest_version, download_url, release_notes = updater.check_for_updates()

                def update_ui_with_result():
                    progress_bar.stop()
                    progress_window.destroy()

                    if is_available:
                        # Show update available dialog
                        self._show_update_dialog(latest_version, download_url, release_notes, updater)
                    else:
                        messagebox.showinfo(
                            "No Updates Available",
                            f"You are running the latest version (v{VERSION})."
                        )

                progress_window.after(0, update_ui_with_result)

            except Exception as e:
                def show_error():
                    progress_bar.stop()
                    progress_window.destroy()
                    messagebox.showerror("Update Check Failed", str(e))

                progress_window.after(0, show_error)

        # Start background thread
        Thread(target=check_updates_thread, daemon=True).start()

    def _show_update_dialog(self, latest_version, download_url, release_notes, updater):
        """Show dialog with update information and install option."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Update Available")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(
            frame,
            text=f"New Version Available: v{latest_version}",
            font=("Arial", 12, "bold")
        ).pack(pady=(0, 10))

        ttk.Label(
            frame,
            text=f"Current Version: v{VERSION}",
            font=("Arial", 10)
        ).pack(pady=(0, 20))

        # Release notes
        ttk.Label(frame, text="Release Notes:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        notes_text = scrolledtext.ScrolledText(frame, height=10, wrap=tk.WORD)
        notes_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        notes_text.insert(tk.END, release_notes)
        notes_text.config(state=tk.DISABLED)

        def install_update():
            """Download and install the update."""
            dialog.destroy()

            if download_url:
                self._download_and_install_update(download_url, updater)
            else:
                # No direct download available - guide user to GitHub
                response = messagebox.askyesno(
                    "Manual Update Required",
                    "Automatic update is not available for your platform.\n\n"
                    f"Would you like to open the GitHub releases page to download v{latest_version} manually?"
                )
                if response:
                    import webbrowser
                    webbrowser.open(f"https://github.com/{updater.GITHUB_REPO}/releases/latest")

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack()

        ttk.Button(btn_frame, text="Install Update", command=install_update).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Later", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def _download_and_install_update(self, download_url, updater):
        """Download and install the update with progress indication."""
        # Create progress window
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Installing Update")
        progress_window.geometry("400x150")
        progress_window.transient(self.root)
        progress_window.grab_set()

        frame = ttk.Frame(progress_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        status_label = ttk.Label(frame, text="Downloading update...", font=("Arial", 10))
        status_label.pack(pady=(0, 20))

        progress_var = tk.IntVar(value=0)
        progress_bar = ttk.Progressbar(frame, mode='determinate', length=300, variable=progress_var, maximum=100)
        progress_bar.pack()

        def update_progress(percent):
            """Update progress bar."""
            progress_var.set(percent)
            status_label.config(text=f"Downloading update... {percent}%")

        def download_and_install_thread():
            """Background thread to download and install update."""
            try:
                # Download
                downloaded_file = updater.download_update(download_url, progress_callback=update_progress)

                def install_phase():
                    status_label.config(text="Installing update...")
                    progress_var.set(100)

                progress_window.after(0, install_phase)

                # Wait a moment for UI update
                time.sleep(0.5)

                # Install
                success = updater.install_update(downloaded_file)

                def show_success():
                    progress_window.destroy()
                    if success:
                        if updater.is_frozen:
                            messagebox.showinfo(
                                "Update Complete",
                                "The application will now restart to complete the update."
                            )
                            # The updater script will restart the app
                            self.root.destroy()
                            sys.exit(0)
                        else:
                            messagebox.showinfo(
                                "Update Complete",
                                "The application has been updated. Please restart the application."
                            )
                            self.root.destroy()
                            sys.exit(0)

                progress_window.after(0, show_success)

            except Exception as e:
                def show_error():
                    progress_window.destroy()
                    messagebox.showerror("Update Failed", f"Failed to install update: {str(e)}")

                progress_window.after(0, show_error)

        # Start background thread
        Thread(target=download_and_install_thread, daemon=True).start()

    def on_closing(self):
        """Handle application closing."""
        # Finish current task if user wants
        if self.current_task and not self.current_task.completed:
            response = messagebox.askyesnocancel(
                "Active Task",
                "You have an active task. Do you want to mark it as complete before exiting?"
            )
            if response is None:  # Cancel
                return
            elif response:  # Yes
                self.current_task.complete()
                self.save_tasks()

        # Stop reminder thread
        self.stop_reminder.set()

        # Close application
        self.root.destroy()


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = WorkLogger(root)
    root.mainloop()


if __name__ == "__main__":
    main()
