#!/usr/bin/env python3
"""
Automated Release Script for Work Logger

This script automates the entire release process:
1. Updates the version in work_logger.py
2. Commits and pushes changes
3. Creates a GitHub release
4. GitHub Actions automatically builds executables

Usage:
    python create_release.py

Or make it executable and run:
    chmod +x create_release.py
    ./create_release.py
"""

import subprocess
import sys
import re
import os
from pathlib import Path


class ReleaseAutomation:
    """Handles automated release creation for Work Logger."""

    def __init__(self):
        self.repo_root = Path(__file__).parent
        self.work_logger_path = self.repo_root / "work_logger.py"
        self.current_version = self._get_current_version()

    def _get_current_version(self):
        """Extract current version from work_logger.py."""
        try:
            with open(self.work_logger_path, 'r') as f:
                content = f.read()
                match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
        except Exception as e:
            print(f"Error reading current version: {e}")
        return None

    def _update_version_in_file(self, new_version):
        """Update VERSION constant in work_logger.py."""
        try:
            with open(self.work_logger_path, 'r') as f:
                content = f.read()

            # Replace the VERSION line
            updated_content = re.sub(
                r'VERSION\s*=\s*["\'][^"\']+["\']',
                f'VERSION = "{new_version}"',
                content
            )

            with open(self.work_logger_path, 'w') as f:
                f.write(updated_content)

            print(f"✓ Updated VERSION to {new_version} in work_logger.py")
            return True
        except Exception as e:
            print(f"✗ Error updating version: {e}")
            return False

    def _validate_version(self, version):
        """Validate version format (e.g., 1.0.0)."""
        pattern = r'^\d+\.\d+\.\d+$'
        return re.match(pattern, version) is not None

    def _check_git_status(self):
        """Check if working directory is clean."""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip() == ""
        except subprocess.CalledProcessError:
            return False

    def _check_gh_cli(self):
        """Check if GitHub CLI is installed."""
        try:
            result = subprocess.run(
                ['gh', '--version'],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✓ GitHub CLI found: {result.stdout.split()[2]}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("✗ GitHub CLI (gh) not found!")
            print("\nPlease install it:")
            print("  Windows: winget install GitHub.cli")
            print("  macOS:   brew install gh")
            print("  Linux:   See https://github.com/cli/cli/blob/trunk/docs/install_linux.md")
            return False

    def _get_user_input(self):
        """Get version and release notes from user."""
        print("=" * 60)
        print("Work Logger - Automated Release Creator")
        print("=" * 60)
        print()

        if self.current_version:
            print(f"Current version: {self.current_version}")
        else:
            print("Warning: Could not detect current version")

        print()

        # Get new version
        while True:
            new_version = input("Enter new version number (e.g., 1.1.0): ").strip()
            if self._validate_version(new_version):
                break
            else:
                print("Invalid version format. Use MAJOR.MINOR.PATCH (e.g., 1.1.0)")

        # Get release notes
        print("\nEnter release notes (press Ctrl+D or Ctrl+Z when done):")
        print("You can use markdown formatting")
        print("-" * 60)

        release_notes = []
        try:
            while True:
                line = input()
                release_notes.append(line)
        except EOFError:
            pass

        release_notes = '\n'.join(release_notes).strip()

        if not release_notes:
            print("\nNo release notes provided. Using default.")
            release_notes = f"Release version {new_version}"

        return new_version, release_notes

    def _commit_and_push(self, version):
        """Commit version change and push to GitHub."""
        try:
            # Stage the modified file
            subprocess.run(['git', 'add', str(self.work_logger_path)], check=True)

            # Commit
            commit_message = f"Bump version to {version}"
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            print(f"✓ Committed version change")

            # Push to main
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            print(f"✓ Pushed to origin/main")

            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Git operation failed: {e}")
            return False

    def _create_github_release(self, version, release_notes):
        """Create GitHub release using gh CLI."""
        try:
            tag = f"v{version}"

            # Create release
            cmd = [
                'gh', 'release', 'create', tag,
                '--title', f"Work Logger v{version}",
                '--notes', release_notes
            ]

            subprocess.run(cmd, check=True)
            print(f"✓ Created GitHub release: {tag}")
            print()
            print("GitHub Actions is now building executables...")
            print("This will take about 5-10 minutes.")
            print()
            print("You can monitor progress at:")
            print("https://github.com/redjoy12/Work-Logger/actions")
            print()
            print("Once complete, users can update via 'Check for Updates' button!")

            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to create release: {e}")
            return False

    def create_release(self):
        """Main function to orchestrate the release process."""
        # Check prerequisites
        if not self._check_gh_cli():
            return False

        # Check if working directory is clean
        if not self._check_git_status():
            print("\n✗ Working directory has uncommitted changes.")
            print("Please commit or stash changes before creating a release.")
            return False

        # Get user input
        new_version, release_notes = self._get_user_input()

        # Confirm
        print("\n" + "=" * 60)
        print("Release Summary:")
        print("=" * 60)
        print(f"Version:       {new_version}")
        print(f"Previous:      {self.current_version}")
        print(f"Release notes: {release_notes[:100]}{'...' if len(release_notes) > 100 else ''}")
        print("=" * 60)

        confirm = input("\nProceed with release? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("Release cancelled.")
            return False

        print("\nStarting release process...\n")

        # Step 1: Update version
        if not self._update_version_in_file(new_version):
            return False

        # Step 2: Commit and push
        if not self._commit_and_push(new_version):
            print("\nRolling back version change...")
            subprocess.run(['git', 'restore', str(self.work_logger_path)])
            return False

        # Step 3: Create GitHub release
        if not self._create_github_release(new_version, release_notes):
            print("\nVersion was updated and pushed, but release creation failed.")
            print("You can create the release manually on GitHub.")
            return False

        print("\n" + "=" * 60)
        print("✓ Release process completed successfully!")
        print("=" * 60)
        return True


def main():
    """Entry point for the release automation script."""
    automation = ReleaseAutomation()

    try:
        success = automation.create_release()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nRelease cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
