#!/usr/bin/env python3
"""
Quick Release Script for Work Logger

This is an alternative, simpler version that reads from a JSON config file.

Usage:
1. Edit release_config.json with your version and notes
2. Run: python quick_release.py
"""

import subprocess
import sys
import json
import re
from pathlib import Path


def read_config():
    """Read release configuration from JSON file."""
    config_path = Path(__file__).parent / "release_config.json"

    if not config_path.exists():
        print("✗ release_config.json not found!")
        print("\nCreating template file...")

        template = {
            "version": "1.1.0",
            "release_notes": "## Features\n- New feature here\n\n## Bug Fixes\n- Bug fix here"
        }

        with open(config_path, 'w') as f:
            json.dump(template, f, indent=2)

        print(f"✓ Created {config_path}")
        print("\nPlease edit release_config.json and run this script again.")
        return None

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        if 'version' not in config or 'release_notes' not in config:
            print("✗ Invalid config file. Must contain 'version' and 'release_notes'")
            return None

        return config
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in config file: {e}")
        return None


def main():
    """Main function."""
    print("=" * 60)
    print("Work Logger - Quick Release")
    print("=" * 60)
    print()

    # Read config
    config = read_config()
    if not config:
        sys.exit(1)

    version = config['version']
    release_notes = config['release_notes']

    print(f"Version: {version}")
    print(f"Notes: {release_notes[:50]}...")
    print()

    confirm = input("Create release? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Cancelled.")
        sys.exit(0)

    # Run the main release script with provided info
    print("\nLaunching full release process...")

    # Import the main automation
    try:
        from create_release import ReleaseAutomation

        automation = ReleaseAutomation()

        # Override user input with config values
        if not automation._check_gh_cli():
            sys.exit(1)

        if not automation._check_git_status():
            print("\n✗ Working directory has uncommitted changes.")
            sys.exit(1)

        # Execute release
        print("\nStarting release process...\n")

        if not automation._update_version_in_file(version):
            sys.exit(1)

        if not automation._commit_and_push(version):
            subprocess.run(['git', 'restore', str(automation.work_logger_path)])
            sys.exit(1)

        if not automation._create_github_release(version, release_notes):
            sys.exit(1)

        print("\n" + "=" * 60)
        print("✓ Release completed successfully!")
        print("=" * 60)

        # Delete or archive config file
        config_path = Path(__file__).parent / "release_config.json"
        archive_path = config_path.with_suffix('.json.used')
        config_path.rename(archive_path)
        print(f"\n✓ Config file archived to {archive_path.name}")

    except ImportError:
        print("✗ Could not import create_release.py")
        sys.exit(1)


if __name__ == "__main__":
    main()
