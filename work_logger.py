#!/usr/bin/env python3
"""
Work Logger - Track your hourly work tasks
A desktop app that reminds you every hour to document what you've been working on.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from datetime import datetime, timedelta
from threading import Thread, Event
import time


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

    DATA_FILE = 'work_log.json'

    def __init__(self, root):
        self.root = root
        self.root.title("Work Logger")
        self.root.geometry("700x600")

        self.tasks = []
        self.current_task = None
        self.reminder_interval = 60 * 60  # 60 minutes in seconds (configurable)
        self.reminder_thread = None
        self.stop_reminder = Event()

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
        self.history_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

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

        if not self.tasks:
            self.history_text.insert(tk.END, "No tasks logged yet.")
        else:
            for i, task in enumerate(reversed(self.tasks), 1):
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

    def save_tasks(self):
        """Save tasks to JSON file."""
        data = {
            'tasks': [task.to_dict() for task in self.tasks],
            'current_task_index': self.tasks.index(self.current_task) if self.current_task in self.tasks else None
        }

        with open(self.DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def load_tasks(self):
        """Load tasks from JSON file."""
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, 'r') as f:
                    data = json.load(f)

                self.tasks = [Task.from_dict(task_data) for task_data in data.get('tasks', [])]

                current_index = data.get('current_task_index')
                if current_index is not None and 0 <= current_index < len(self.tasks):
                    self.current_task = self.tasks[current_index]
                    # If loaded task is marked complete, set current to None
                    if self.current_task.completed:
                        self.current_task = None

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
