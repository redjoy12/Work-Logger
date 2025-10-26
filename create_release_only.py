#!/usr/bin/env python3
"""
Create GitHub Release Only

This script creates a GitHub release for an already-pushed version.
Useful when the version was bumped and pushed but release creation failed.

Usage:
    python create_release_only.py
"""

import subprocess
import sys

def create_release():
    """Create a GitHub release for the current version."""
    print("=" * 60)
    print("Create GitHub Release Only")
    print("=" * 60)
    print("\nThis will create a release for an already-committed version.")
    print()

    # Get version
    version = input("Enter version number (e.g., 1.0.1): ").strip()

    # Get release notes
    print("\nEnter release notes (markdown supported):")
    print("Type 'END' on a new line when finished")
    print("-" * 60)

    release_notes = []
    while True:
        try:
            line = input()
            if line.strip().upper() == 'END':
                break
            release_notes.append(line)
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\n\nCancelled.")
            return False

    release_notes = '\n'.join(release_notes).strip()

    if not release_notes:
        release_notes = f"Release version {version}"

    # Confirm
    print("\n" + "=" * 60)
    print(f"Version: {version}")
    print(f"Tag: v{version}")
    print(f"Notes: {release_notes[:100]}...")
    print("=" * 60)

    confirm = input("\nCreate release? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Cancelled.")
        return False

    # Create release
    try:
        tag = f"v{version}"
        cmd = [
            'gh', 'release', 'create', tag,
            '--title', f"Work Logger v{version}",
            '--notes', release_notes
        ]

        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        print(f"\n✓ Created GitHub release: {tag}")
        print()
        print("GitHub Actions is now building executables...")
        print("This will take about 5-10 minutes.")
        print()
        print("You can monitor progress at:")
        print("https://github.com/redjoy12/Work-Logger/actions")

        return True

    except subprocess.CalledProcessError as e:
        print(f"\n✗ Failed to create release: {e}")
        if e.stderr:
            print(f"\nError output:")
            print(e.stderr)
        if e.stdout:
            print(f"\nStandard output:")
            print(e.stdout)

        print("\nCommon issues and solutions:")
        print("  1. Not authenticated:")
        print("     Run: gh auth login")
        print()
        print("  2. No permission:")
        print("     Make sure you have write access to the repository")
        print()
        print("  3. Tag already exists:")
        print("     Run: gh release list")
        print("     Delete with: gh release delete v{version}")

        return False
    except FileNotFoundError:
        print("\n✗ GitHub CLI (gh) not found!")
        print("\nInstall it:")
        print("  Windows: winget install GitHub.cli")
        print("  macOS:   brew install gh")
        print("  Linux:   See https://github.com/cli/cli/blob/trunk/docs/install_linux.md")
        return False


if __name__ == "__main__":
    try:
        success = create_release()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(1)
