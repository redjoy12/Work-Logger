# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.4] - 2025-11-03

### Fixed
- Fixed fullscreen UI centering and modernized reminder window for better user experience
- Fixed all pylint issues across Python files for improved code quality
- Resolved remaining pylint issues in updater.py and work_logger.py

### Improved
- Improved work history entry clarity with better selection overlay
- Enhanced code quality with comprehensive linting fixes

### Added
- Added Bandit security scan workflow to GitHub Actions for automated security checks
- Updated Python versions in pylint workflow to ensure compatibility

## [1.0.3] - 2025-11-03

### Improved
- Improved work history entry clarity and selection overlay
- Enhanced UI design with modern styling and color scheme
- Added task management improvements and UI updates

### Added
- Automated security scanning with Bandit
- Updated CI/CD workflows with latest Python versions

### Fixed
- Fixed various UI and code quality issues

## [1.0.2] - Earlier Release

### Fixed
- Cleaned up project structure and removed unnecessary files
- Improved error reporting in release script
- Fixed release script to handle duplicate version and empty commits

## [1.0.1] - Earlier Release

### Fixed
- Fixed encoding error when creating releases with Unicode characters
- Fixed release notes input handling for Windows

## [1.0.0] - Initial Release

### Added
- Work Logger application with hourly task tracking
- Pop-up reminders for task logging
- Automatic update functionality with GitHub integration
- Log management features and daily file storage
- Support for building standalone .exe executables
- Automated executable builds with GitHub Actions
- Fully automated release creation scripts
