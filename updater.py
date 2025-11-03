"""
Auto-updater module for Work Logger
Handles checking for updates and downloading new versions from GitHub
"""

import os
import sys
import json
import subprocess
import platform
from urllib import request
from urllib.error import URLError
import tempfile


class Updater:
    """Handles application updates from GitHub releases."""

    GITHUB_REPO = "redjoy12/Work-Logger"
    GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

    def __init__(self, current_version):
        self.current_version = current_version
        self.is_frozen = getattr(sys, 'frozen', False)  # True if running as .exe

    def check_for_updates(self):
        """
        Check if a new version is available on GitHub.
        Returns: (is_available, latest_version, download_url, release_notes)
        """
        try:
            # Fetch latest release info from GitHub
            req = request.Request(self.GITHUB_API_URL)
            req.add_header('Accept', 'application/vnd.github.v3+json')

            with request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))

            latest_version = data.get('tag_name', '').lstrip('v')
            release_notes = data.get('body', 'No release notes available.')

            if not latest_version:
                return False, None, None, None

            # Compare versions
            is_newer = self._is_newer_version(latest_version, self.current_version)

            if not is_newer:
                return False, latest_version, None, release_notes

            # Find appropriate download URL based on platform and execution mode
            download_url = self._get_download_url(data.get('assets', []))

            return True, latest_version, download_url, release_notes

        except (URLError, json.JSONDecodeError, KeyError) as e:
            raise Exception(f"Failed to check for updates: {str(e)}") from e

    def _is_newer_version(self, latest, current):
        """Compare version strings (e.g., '1.2.3' vs '1.2.2')."""
        def version_tuple(v):
            return tuple(map(int, v.split('.')))

        try:
            return version_tuple(latest) > version_tuple(current)
        except (ValueError, AttributeError):
            return False

    def _get_download_url(self, assets):
        """Get the appropriate download URL for current platform and execution mode."""
        system = platform.system()

        if self.is_frozen:
            # Running as executable - download executable
            if system == "Windows":
                # Look for .exe file
                for asset in assets:
                    if asset['name'].endswith('.exe'):
                        return asset['browser_download_url']
            elif system == "Darwin":
                # Look for macOS binary
                for asset in assets:
                    if 'macos' in asset['name'].lower() or 'darwin' in asset['name'].lower():
                        return asset['browser_download_url']
            elif system == "Linux":
                # Look for Linux binary
                for asset in assets:
                    if 'linux' in asset['name'].lower() and not asset['name'].endswith('.exe'):
                        return asset['browser_download_url']

        # Fallback: return source code archive or None
        for asset in assets:
            if asset['name'] == 'Source code (zip)':
                return asset['zipball_url']

        return None

    def download_update(self, download_url, progress_callback=None):
        """
        Download the update file.
        Returns: path to downloaded file
        """
        try:
            # Create temp file
            suffix = '.exe' if download_url.endswith('.exe') else '.zip'
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_path = temp_file.name

            # Download with progress
            def report_progress(block_num, block_size, total_size):
                if progress_callback and total_size > 0:
                    downloaded = block_num * block_size
                    percent = min(100, int((downloaded / total_size) * 100))
                    progress_callback(percent)

            request.urlretrieve(download_url, temp_path, reporthook=report_progress)

            return temp_path

        except (URLError, IOError, OSError) as e:
            raise Exception(f"Failed to download update: {str(e)}") from e

    def install_update(self, downloaded_file):
        """
        Install the downloaded update.
        For executables: replaces current .exe and restarts
        For Python scripts: uses git pull
        """
        if self.is_frozen and downloaded_file.endswith('.exe'):
            # Running as .exe - need to replace executable
            return self._install_exe_update(downloaded_file)
        # Running as Python script - use git
        return self._install_git_update()

    def _install_exe_update(self, new_exe_path):
        """
        Replace current executable with new one.
        Creates a batch/shell script to replace the file after exit.
        """
        current_exe = sys.executable
        system = platform.system()

        if system == "Windows":
            # Create batch script to replace exe and restart
            with tempfile.NamedTemporaryFile(delete=False, suffix='.bat') as script_file:
                script_path = script_file.name

            script_content = f'''@echo off
echo Updating Work Logger...
timeout /t 2 /nobreak > nul
copy /y "{new_exe_path}" "{current_exe}"
del "{new_exe_path}"
echo Update complete! Restarting...
start "" "{current_exe}"
del "%~f0"
'''

            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)

            # Start the update script
            subprocess.Popen(['cmd.exe', '/c', script_path],
                           creationflags=subprocess.CREATE_NO_WINDOW)

            return True

        # Unix-like system (Linux/macOS)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.sh') as script_file:
            script_path = script_file.name

        script_content = f'''#!/bin/bash
sleep 2
cp "{new_exe_path}" "{current_exe}"
chmod +x "{current_exe}"
rm "{new_exe_path}"
"{current_exe}" &
rm "$0"
'''

        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)

        os.chmod(script_path, 0o755)

        subprocess.Popen(['/bin/bash', script_path])

        return True

    def _install_git_update(self):
        """Use git pull to update the application (for Python script mode)."""
        try:
            # Check if we're in a git repository
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True, text=True, check=False
            )

            if result.returncode != 0:
                raise RuntimeError(
                    "Not in a git repository. Please download manually from GitHub."
                )

            # Fetch and pull latest changes
            subprocess.run(['git', 'fetch', 'origin'], check=True, capture_output=True)
            subprocess.run(['git', 'pull', 'origin', 'main'], check=True, capture_output=True)

            return True

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git update failed: {str(e)}") from e
        except FileNotFoundError as exc:
            raise RuntimeError(
                "Git is not installed. Please install git or download manually from GitHub."
            ) from exc
