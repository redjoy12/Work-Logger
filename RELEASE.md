# Release Process for Work Logger

This document explains how the automated build and update system works.

## How the Update System Works

When users click the "Check for Updates" button in the app:
1. The app queries GitHub for the latest release
2. If a new version is found, it downloads the appropriate executable (.exe for Windows, binaries for Linux/macOS)
3. The app replaces itself with the new version and restarts

## Creating a New Release (Fully Automated!)

We have **two automated methods** for creating releases. Choose the one you prefer:

### Method 1: Interactive Script (Recommended)

The simplest way! Just run one command and answer a few questions:

**Windows:**
```batch
release.bat
```
Double-click `release.bat` or run it from command prompt.

**Linux/macOS:**
```bash
chmod +x release.sh
./release.sh
```

**Or directly:**
```bash
python create_release.py
```

The script will:
1. Show your current version
2. Ask for the new version number (e.g., `1.1.0`)
3. Ask for release notes (type them and press Ctrl+D/Ctrl+Z when done)
4. Show a summary and ask for confirmation
5. Automatically:
   - Update `VERSION` in `work_logger.py`
   - Commit and push changes
   - Create GitHub release with tag
   - Trigger GitHub Actions to build executables

**That's it!** In 5-10 minutes, users can update via "Check for Updates"!

### Method 2: Config File (Even Simpler!)

For those who prefer editing a file over typing into a terminal:

1. **Create/Edit** `release_config.json`:
   ```json
   {
     "version": "1.1.0",
     "release_notes": "## Features\n- New dark mode\n- Export to CSV\n\n## Bug Fixes\n- Fixed crash on startup"
   }
   ```

2. **Run the quick release script:**
   ```bash
   python quick_release.py
   ```

3. **Confirm** and it's done!

The config file will be automatically archived after use so you start fresh next time.

### Prerequisites

Both methods require:
- **GitHub CLI (`gh`)** to be installed and authenticated
- **Clean git working directory** (no uncommitted changes)

#### Installing GitHub CLI

If you don't have `gh` installed:

**Windows:**
```bash
winget install GitHub.cli
```

**macOS:**
```bash
brew install gh
```

**Linux:**
See [GitHub CLI installation guide](https://github.com/cli/cli/blob/trunk/docs/install_linux.md)

**Authenticate:**
```bash
gh auth login
```

### What Happens Automatically

Once you run either script:

1. ✓ Version updated in `work_logger.py`
2. ✓ Changes committed with message "Bump version to X.X.X"
3. ✓ Changes pushed to GitHub
4. ✓ GitHub release created with tag `vX.X.X`
5. ✓ GitHub Actions builds executables (Windows, Linux, macOS)
6. ✓ Executables uploaded as release assets
7. ✓ Users can now update via the app!

The entire process takes about 5-10 minutes (mostly waiting for builds).

## Manual Build (For Testing)

If you want to build the executable locally for testing:

```bash
python build_exe.py
```

The executable will be in the `dist/` folder.

## Triggering Builds Manually

You can also trigger the build workflow manually without creating a release:

1. Go to the "Actions" tab on GitHub
2. Select "Build and Release" workflow
3. Click "Run workflow"
4. Choose the branch and click "Run workflow"

Note: Manual builds won't upload to releases automatically - this is mainly for testing.

## Version Naming Convention

- Use semantic versioning: `MAJOR.MINOR.PATCH`
  - MAJOR: Breaking changes (1.0.0 → 2.0.0)
  - MINOR: New features (1.0.0 → 1.1.0)
  - PATCH: Bug fixes (1.0.0 → 1.0.1)
- Always prefix tags with 'v' (e.g., v1.0.0)
- Keep the version in `work_logger.py` in sync with the release tag

## Troubleshooting

### Build Failed

Check the Actions tab on GitHub to see the error logs. Common issues:
- Missing dependencies in `work_logger.spec`
- Syntax errors in the code
- PyInstaller compatibility issues

### Users Can't Update

Make sure:
- The release tag starts with 'v' (e.g., v1.0.0)
- The build workflow completed successfully
- The executable files are attached to the release
- The version in `work_logger.py` is updated

### Testing Before Release

1. Build locally: `python build_exe.py`
2. Test the executable in `dist/`
3. If it works, proceed with creating the GitHub release
