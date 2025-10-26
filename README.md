# Work-Logger

A desktop application that helps you track and document what you've been working on throughout the day. Get reminded every hour (or at custom intervals) to log your tasks with an attention-grabbing pop-up notification.

## Features

- **Hourly Reminders**: Get pop-up notifications at regular intervals to remind you to document your work
- **Task Tracking**: Log tasks with automatic timestamps
- **Task Management**: Mark tasks as complete and start new ones seamlessly
- **Persistent Storage**: All your work logs are saved automatically to daily JSON files
- **Task History**: View your complete work history with timestamps and durations
- **Customizable Intervals**: Set reminder intervals from 1 minute to 4 hours
- **Attention-Grabbing Alerts**: Pop-up windows that appear on top and flash to get your attention
- **Auto-Update**: Built-in automatic update checker that downloads and installs new versions from GitHub
- **Edit & Delete Tasks**: Modify or remove tasks from your history
- **Daily Log Files**: Tasks are organized into daily log files for better management

## Requirements

- Python 3.6 or higher
- Tkinter (comes pre-installed with Python on most systems)

No additional dependencies required!

## Installation

### Option 1: Run as Python Script

1. Clone this repository:
```bash
git clone https://github.com/yourusername/Work-Logger.git
cd Work-Logger
```

2. Make sure you have Python 3 installed:
```bash
python3 --version
```

### Option 2: Download Pre-built Executable (Recommended for Non-Developers)

The easiest way to use Work Logger is to download the pre-built executable:

1. Go to the [Releases page](https://github.com/redjoy12/Work-Logger/releases/latest)
2. Download the appropriate file for your operating system:
   - **Windows**: `WorkLogger-vX.X.X-windows.exe`
   - **Linux**: `WorkLogger-vX.X.X-linux.tar.gz`
   - **macOS**: `WorkLogger-vX.X.X-macos.tar.gz`
3. Run the executable:
   - **Windows**: Double-click the .exe file
   - **Linux/macOS**: Extract the archive and run the binary
4. The app will automatically check for updates and can update itself!

**Note:** Pre-built executables are automatically created by GitHub Actions whenever a new release is published.

### Option 3: Build Standalone Executable Locally

If you want to build the executable yourself or customize the build:

1. Clone this repository (if not already done):
```bash
git clone https://github.com/redjoy12/Work-Logger.git
cd Work-Logger
```

2. Install PyInstaller (if not already installed):
```bash
pip install pyinstaller
```

3. Build the executable using one of these methods:

   **Method A: Using the Python build script (recommended)**
   ```bash
   python build_exe.py
   ```

   **Method B: Using the Windows batch file**
   ```batch
   build_exe.bat
   ```

   **Method C: Manual build with PyInstaller**
   ```bash
   pyinstaller work_logger.spec
   ```

4. After building, find your executable at:
   ```
   dist/WorkLogger.exe  # Windows
   dist/WorkLogger      # Linux/macOS
   ```

5. You can now:
   - Double-click the executable to run the application
   - Copy the file anywhere on your computer
   - Share it with others (no Python installation required!)
   - Add it to your system's Startup folder for automatic launch

**Note:** The executable is completely standalone and doesn't require Python to be installed.

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

5. **Check for Updates**:
   - Click "Check for Updates" button in the settings section
   - The app will check GitHub for new releases
   - If an update is available, you'll see release notes and can install it automatically
   - For standalone .exe files, the app will download and replace itself
   - For Python script mode, it will use git pull to update

6. **View Task History**:
   - The bottom section shows all your logged tasks
   - View start/end times, durations, and completion status
   - Click on any task to select it, then use "Edit Selected Task" or "Delete Selected Task"

### Data Storage

All tasks are automatically saved to daily JSON files in the `logs/` directory:
- `logs/YYYY-MM-DD.json` - Tasks for each day
- `logs/current_task.json` - Reference to the currently active task

Each log file contains:
- Task descriptions
- Start and end timestamps
- Completion status
- Duration information

The application automatically migrates old `work_log.json` format to the new daily files structure.

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

**If using the .exe file:**
1. Build the executable (see Installation section)
2. Press `Win+R`, type `shell:startup`, press Enter
3. Copy `WorkLogger.exe` or create a shortcut to it in the Startup folder

**If using the Python script:**
1. Create a shortcut to `work_logger.py`
2. Press `Win+R`, type `shell:startup`, press Enter
3. Move the shortcut to the Startup folder

## For Developers: Creating Releases

Creating a new release is **fully automated**! Just run one script:

### Quick Start

**Windows** (double-click or run):
```batch
release.bat
```

**Linux/macOS**:
```bash
./release.sh
```

**Direct**:
```bash
python create_release.py
```

The script will:
1. Ask for the new version number
2. Ask for release notes
3. Automatically update code, commit, push, and create GitHub release
4. GitHub Actions builds executables for Windows, Linux, and macOS
5. Users can update via "Check for Updates" button!

### Alternative: Config File Method

Edit `release_config.json`:
```json
{
  "version": "1.2.0",
  "release_notes": "## Features\n- Cool new feature"
}
```

Then run:
```bash
python quick_release.py
```

### What You Need

- **GitHub CLI** (`gh`) installed and authenticated
  - Windows: `winget install GitHub.cli`
  - macOS: `brew install gh`
  - Linux: See [installation guide](https://github.com/cli/cli/blob/trunk/docs/install_linux.md)
- Run `gh auth login` to authenticate

That's it! The entire release process takes about 5-10 minutes.

See [RELEASE.md](RELEASE.md) for detailed instructions and troubleshooting.

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

### Version 1.0.0 (Current)
- **Auto-Update Feature**: Built-in update checker and installer
  - Checks GitHub releases for new versions
  - Displays release notes before updating
  - Automatically downloads and installs updates
  - Works with both .exe files and Python scripts
- **Task Management**: Edit and delete tasks
- **Daily Log Files**: Tasks organized into daily JSON files
- **Data Migration**: Automatic migration from old format
- Basic task tracking functionality
- Hourly reminder system with customizable intervals
- Task persistence with automatic saving
- Complete task history view with timestamps and durations