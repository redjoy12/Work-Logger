# Release Process for Work Logger

This document explains how the automated build and update system works.

## How the Update System Works

When users click the "Check for Updates" button in the app:
1. The app queries GitHub for the latest release
2. If a new version is found, it downloads the appropriate executable (.exe for Windows, binaries for Linux/macOS)
3. The app replaces itself with the new version and restarts

## Creating a New Release (Automated Build)

Thanks to GitHub Actions, creating a new release is simple! Here's how:

### Step 1: Update the Version Number

Edit `work_logger.py` and update the VERSION constant:

```python
VERSION = "1.1.0"  # Change this to your new version
```

### Step 2: Commit and Push Your Changes

```bash
git add .
git commit -m "Bump version to 1.1.0 and add new features"
git push origin main
```

### Step 3: Create a GitHub Release

1. Go to your repository on GitHub: https://github.com/redjoy12/Work-Logger
2. Click on "Releases" in the right sidebar
3. Click "Draft a new release"
4. Create a new tag: `v1.1.0` (must start with 'v' and match the version in code)
5. Set the release title: `Work Logger v1.1.0`
6. Add release notes describing what's new
7. Click "Publish release"

### Step 4: Wait for Automated Build

Once you publish the release, GitHub Actions will automatically:
- Build the Windows .exe file
- Build the Linux binary
- Build the macOS binary
- Upload all three as release assets

This takes about 5-10 minutes. You can watch the progress in the "Actions" tab.

### Step 5: Users Can Now Update

Once the build is complete, users can click "Check for Updates" in the app and they'll automatically download and install the new version!

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
