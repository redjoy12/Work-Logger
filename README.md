# Work-Logger

A desktop application that helps you track and document what you've been working on throughout the day. Get reminded every hour (or at custom intervals) to log your tasks with an attention-grabbing pop-up notification.

## Features

- **Hourly Reminders**: Get pop-up notifications at regular intervals to remind you to document your work
- **Task Tracking**: Log tasks with automatic timestamps
- **Task Management**: Mark tasks as complete and start new ones seamlessly
- **Persistent Storage**: All your work logs are saved automatically to a JSON file
- **Task History**: View your complete work history with timestamps and durations
- **Customizable Intervals**: Set reminder intervals from 1 minute to 4 hours
- **Attention-Grabbing Alerts**: Pop-up windows that appear on top and flash to get your attention

## Requirements

- Python 3.6 or higher
- Tkinter (comes pre-installed with Python on most systems)

No additional dependencies required!

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/Work-Logger.git
cd Work-Logger
```

2. Make sure you have Python 3 installed:
```bash
python3 --version
```

## Usage

### Starting the Application

Run the application with:
```bash
python3 work_logger.py
```

Or make it executable and run directly:
```bash
chmod +x work_logger.py
./work_logger.py
```

### How to Use

1. **Start a New Task**:
   - Type your task description in the "What are you working on?" field
   - Click "Start New Task" or press Enter
   - The task begins tracking automatically

2. **Finish Current Task and Start New**:
   - When you're done with a task, type your next task
   - Click "Finish Current & Start New" to complete the current task and begin the new one

3. **Respond to Reminders**:
   - Every hour (or at your set interval), a pop-up will appear
   - You can:
     - **Log Task**: Quickly log what you've been working on
     - **Open Main Window**: Open the main application to see full details
     - **Remind Me Later**: Dismiss the reminder (it will appear again at the next interval)

4. **Adjust Reminder Interval**:
   - Change the "Reminder Interval (minutes)" value
   - Click "Update Interval" to apply
   - Use "Test Reminder Now" to see what the reminder looks like

5. **View Task History**:
   - The bottom section shows all your logged tasks
   - View start/end times, durations, and completion status

### Data Storage

All tasks are automatically saved to `work_log.json` in the application directory. This file contains:
- Task descriptions
- Start and end timestamps
- Completion status
- Duration information

## Screenshots

### Main Window
The main window shows your current task, allows you to start new tasks, and displays your task history.

### Reminder Pop-up
The reminder window appears on top of all other windows and flashes to get your attention.

## Tips

- **Use Descriptive Task Names**: Include what you're working on and the goal
  - Good: "Implementing user authentication API endpoint"
  - Better than: "Coding"

- **Set Realistic Intervals**: 60 minutes is default, but adjust based on your workflow
  - For focused work sessions: 25-30 minutes (Pomodoro style)
  - For general tracking: 60 minutes
  - For high-level tracking: 120+ minutes

- **Review Your History**: Use the task history to:
  - Fill out timesheets
  - Track productivity patterns
  - Write status reports
  - Understand where your time goes

## Troubleshooting

### Application won't start
- Ensure Python 3.6+ is installed
- On some Linux systems, install tkinter: `sudo apt-get install python3-tk`

### Reminders not appearing
- Check that the application is running in the background
- Test the reminder with "Test Reminder Now"
- Verify your interval setting

### Data not saving
- Ensure the application has write permissions in its directory
- Check that `work_log.json` can be created/modified

## Advanced Usage

### Running on Startup (Linux)

Create a desktop entry:
```bash
cat > ~/.config/autostart/work-logger.desktop << EOF
[Desktop Entry]
Type=Application
Name=Work Logger
Exec=python3 /path/to/Work-Logger/work_logger.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
```

### Running on Startup (macOS)

Use Automator to create a Launch Agent or add to Login Items in System Preferences.

### Running on Startup (Windows)

1. Create a shortcut to `work_logger.py`
2. Press `Win+R`, type `shell:startup`, press Enter
3. Move the shortcut to the Startup folder

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## License

This project is licensed under the terms included in the LICENSE file.

## Author

Created to help developers and knowledge workers track their daily work activities.

## Changelog

### Version 1.0.0 (Initial Release)
- Basic task tracking functionality
- Hourly reminder system
- Task persistence
- Task history view
- Customizable reminder intervals