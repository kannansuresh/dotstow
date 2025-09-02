#!/usr/bin/env python3
"""
Dotfile Mover Script

Moves existing configuration files/directories into a GNU Stow-compatible
dotfiles repository structure, optionally runs stow, and cleans up junk files.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional
import logging
import json

# Configure logging for clear output
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


def check_stow_is_installed() -> bool:
    """Checks if the 'stow' command is available in the system's PATH."""
    return shutil.which("stow") is not None


class DotfileMover:
    """Handles the moving of dotfiles to a Stow-compatible repository."""

    # A more complete and organized list of common dotfiles/config directories
    # The key is the path relative to the home directory, the value is the app name.
    APP_NAME_MAPPINGS = {
        # Shells
        ".zshrc": "zsh",
        ".bashrc": "bash",
        ".bash_profile": "bash",
        ".bash_aliases": "bash",
        ".profile": "shell",
        ".login": "shell",
        "config.fish": "fish",
        # Editors
        ".vimrc": "vim",
        ".gvimrc": "gvim",
        ".config/nvim": "nvim",
        ".ideavimrc": "ideavim",
        ".nanorc": "nano",
        # Git
        ".gitconfig": "git",
        ".gitignore_global": "git",
        ".config/git": "git",
        # Terminal Multiplexers
        ".tmux.conf": "tmux",
        ".screenrc": "screen",
        # Terminal Emulators
        ".config/alacritty": "alacritty",
        ".config/kitty": "kitty",
        ".config/ghostty": "ghostty",
        # Window Managers & Desktop Environment
        ".xprofile": "xorg",
        ".Xresources": "xorg",
        ".Xmodmap": "xorg",
        ".xinitrc": "xorg",
        ".config/i3": "i3",
        ".config/polybar": "polybar",
        # Other Common Applications
        ".config/starship.toml": "starship",
        ".config/direnv": "direnv",
        ".ssh": "ssh",
        ".gnupg": "gnupg",
        ".config/htop": "htop",
        ".config/npm": "npm",
        ".config/pip": "pip",
        ".config/gem": "gem",
        ".inputrc": "readline",
        ".pylintrc": "pylint",
    }

    def __init__(
        self,
        source_path: str,
        app_name: Optional[str] = None,
        dotfiles_dir: Optional[str] = None,
        auto_stow: bool = False,
        no_stow: bool = False,
    ):
        self.source_path = Path(source_path).expanduser().resolve()
        self.app_name = app_name

        # Load configuration file first
        config = self._load_config()
        config_dir = config.get("dotfiles_dir")

        # Determine the dotfiles directory based on priority
        # 1. Command line argument
        # 2. Config file entry
        # 3. Interactive prompt (handled by _get_dotfiles_dir)
        final_dotfiles_dir = dotfiles_dir or config_dir
        self.dotfiles_dir = self._get_dotfiles_dir(final_dotfiles_dir)

        self.auto_stow = auto_stow
        self.no_stow = no_stow

    def _get_global_config_path(self) -> Path:
        """Returns the expected path to the global configuration file."""
        return Path.home() / ".config" / "dotstow" / "config.json"

    def _get_local_config_path(self) -> Path:
        """Returns the expected path to the local configuration file."""
        return Path.cwd() / "config.json"

    def _load_config(self) -> dict:
        """Loads configuration from a JSON file, checking global and local paths."""
        global_config_path = self._get_global_config_path()
        local_config_path = self._get_local_config_path()

        if global_config_path.exists():
            log.info(f"Using global configuration file: {global_config_path}")
            config_path = global_config_path
        elif local_config_path.exists():
            log.info(f"Using local configuration file: {local_config_path}")
            config_path = local_config_path
        else:
            log.info("No configuration file found. Using defaults.")
            return {}

        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            log.warning(f"Invalid JSON in configuration file: {config_path}")
            return {}
        except Exception as e:
            log.warning(f"Failed to read configuration file: {e}")
            return {}

    def _get_dotfiles_dir(self, dotfiles_dir: Optional[str]) -> Path:
        """Determines the dotfiles directory with smart defaults and user input."""
        if dotfiles_dir:
            path = Path(dotfiles_dir).expanduser().resolve()
            if not path.exists():
                raise ValueError(f"Specified dotfiles directory does not exist: {path}")
            return path

        current_dir = Path.cwd()
        if self._is_dotfiles_directory(current_dir):
            log.info(f"Using current directory as dotfiles repo: {current_dir}")
            return current_dir

        # Fallback to interactive mode if no directory is specified and current dir is not a repo
        default_path = Path.home() / "dotfiles"
        path = default_path

        try:
            while True:
                if not path.exists():
                    create_default = input(
                        f"Dotfiles directory '{path}' does not exist. Create it? [y/N]: "
                    ).lower()
                    if create_default in ("y", "yes"):
                        path.mkdir(parents=True, exist_ok=True)
                        log.info(f"Created dotfiles directory: {path}")
                        return path
                    else:
                        new_path_str = input(
                            "Please provide an alternative dotfiles directory path: "
                        ).strip()
                        if not new_path_str:
                            log.error("No path provided.")
                            continue
                        path = Path(new_path_str).expanduser().resolve()
                else:
                    return path
        except (KeyboardInterrupt, EOFError):
            log.error("\nOperation cancelled.")
            sys.exit(0)

    def _is_dotfiles_directory(self, path: Path) -> bool:
        """
        Heuristically checks if a directory looks like a dotfiles repository.
        This helps in auto-detecting the location if the user is already there.
        """
        # A directory named 'dotfiles' or similar
        if path.name.lower() in ("dotfiles", "configs", "config"):
            return True
        # Presence of common stow-related files
        if (path / ".stow-local-ignore").exists() or (
            path / ".stow-global-ignore"
        ).exists():
            return True
        # Presence of multiple application directories
        app_dirs = [d for d in path.iterdir() if d.is_dir()]
        stowable_dirs = [
            d for d in app_dirs if d.name in self.APP_NAME_MAPPINGS.values()
        ]
        return len(stowable_dirs) >= 2

    def _infer_app_name(self) -> str:
        """
        Infers the application name from the source path by checking a mapping
        or by inspecting the directory structure.
        """
        home = Path.home()
        relative_path_str = str(self.source_path.relative_to(home))

        for path_key, app_name in self.APP_NAME_MAPPINGS.items():
            if relative_path_str.startswith(path_key):
                return app_name

        # Fallback for complex paths
        if relative_path_str.startswith(".config"):
            try:
                # e.g., for ~/.config/my-app/file -> my-app
                return self.source_path.relative_to(home / ".config").parts[0]
            except ValueError:
                pass  # Fall through

        return self.source_path.name.lstrip(".")

    def _get_target_path(self, app_name: str) -> Path:
        """Calculates the target path in the dotfiles repository, preserving .config structure."""
        home = Path.home()
        relative_path = self.source_path.relative_to(home)

        # Check if the path is inside the .config directory
        if relative_path.parts[0] == ".config":
            # The target path should be dotfiles_dir/app_name/.config/relative_path_from_.config
            config_subpath = relative_path.relative_to(".config")
            return self.dotfiles_dir / app_name / ".config" / config_subpath
        else:
            # For all other cases, move the dotfile directly into the app directory
            return self.dotfiles_dir / app_name / relative_path

    def _validate_source_and_target(self) -> None:
        """Validates source existence and target path availability."""
        if not self.source_path.exists():
            raise FileNotFoundError(f"Source path does not exist: {self.source_path}")

        if self.source_path.is_symlink():
            log.warning("Source path is already a symlink. No action needed.")
            sys.exit(0)

        # Check if source is already inside the dotfiles repo
        try:
            self.source_path.relative_to(self.dotfiles_dir)
            log.warning(
                "Source path is already inside the dotfiles directory. Skipping move."
            )
            sys.exit(0)
        except ValueError:
            pass  # Expected if the paths are not related

        # Calculate target path and check for conflicts
        self.app_name = self.app_name or self._infer_app_name()
        self.target_path = self._get_target_path(self.app_name)

        if self.target_path.exists():
            raise FileExistsError(
                f"Target path already exists: {self.target_path}.\n"
                "Please move it manually or specify a different app name."
            )

    def _perform_movement(self) -> None:
        """Executes the file/directory move operation."""
        try:
            self.target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(self.source_path), str(self.target_path))
            log.info(
                f"✓ Successfully moved '{self.source_path.name}' to {self.target_path.parent}"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to move files: {e}")

    def _run_stow(self) -> None:
        """Runs stow to symlink the moved application files."""
        log.info(f"Running stow for '{self.app_name}'...")
        try:
            subprocess.run(
                [
                    "stow",
                    "-d",
                    str(self.dotfiles_dir),
                    "-t",
                    str(Path.home()),
                    self.app_name,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            log.info(f"✓ Stow completed for '{self.app_name}'.")
        except subprocess.CalledProcessError as e:
            log.error(f"Stow failed with exit code {e.returncode}:")
            log.error(f"Stdout:\n{e.stdout}")
            log.error(f"Stderr:\n{e.stderr}")
            sys.exit(1)

    def move(self) -> None:
        """Main execution flow for moving and stowing dotfiles."""
        self._validate_source_and_target()

        log.info("--- Preparing Dotfile Move ---")
        log.info(f"Source:      {self.source_path}")
        log.info(f"App name:    {self.app_name}")
        log.info(f"Dotfiles:    {self.dotfiles_dir}")
        log.info(f"Target:      {self.target_path}")

        try:
            if input("Proceed with movement? [y/N]: ").lower() not in ("y", "yes"):
                log.info("Movement cancelled.")
                return
        except (KeyboardInterrupt, EOFError):
            log.error("\nMovement cancelled.")
            sys.exit(0)

        self._perform_movement()

        # Handle stow logic based on flags
        if self.no_stow:
            log.info("Stow skipped due to --no-stow flag.")
        elif self.auto_stow:
            self._run_stow()
        else:
            try:
                if input("Run `stow` now to create symlinks? [y/N]: ").lower() in (
                    "y",
                    "yes",
                ):
                    self._run_stow()
                else:
                    log.info("Stow skipped. You can run it manually later.")
            except (KeyboardInterrupt, EOFError):
                log.info("\nStow cancelled.")


def create_parser() -> argparse.ArgumentParser:
    """Creates the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Move configuration files to GNU Stow-compatible dotfiles repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Move a file, infer app name, and use the default dotfiles directory
  %(prog)s ~/.gitconfig

  # Move a directory, specify the app name
  %(prog)s ~/.config/nvim nvim

  # Specify a custom dotfiles directory and automatically run stow
  %(prog)s ~/.config/alacritty --dotfiles-dir ~/my-dotfiles --auto-stow
        """,
    )

    parser.add_argument(
        "source_path", help="Path to configuration file/directory to move"
    )
    parser.add_argument(
        "app_name",
        nargs="?",
        help="Application directory name (auto-inferred if not provided)",
    )
    parser.add_argument(
        "--dotfiles-dir",
        "-d",
        help="Path to dotfiles repository (auto-detected if run from dotfiles dir)",
    )
    parser.add_argument(
        "--auto-stow",
        action="store_true",
        help="Run stow automatically after the move without confirmation",
    )
    parser.add_argument(
        "--no-stow",
        action="store_true",
        help="Skip running stow completely",
    )
    return parser


def main() -> None:
    """Main entry point of the script."""
    parser = create_parser()
    args = parser.parse_args()

    if not check_stow_is_installed():
        log.error("GNU Stow is not installed or not found in PATH.")
        log.error("Please install it and try again.")
        sys.exit(1)

    try:
        mover = DotfileMover(
            source_path=args.source_path,
            app_name=args.app_name,
            dotfiles_dir=args.dotfiles_dir,
            auto_stow=args.auto_stow,
            no_stow=args.no_stow,
        )
        mover.move()
    except (FileNotFoundError, FileExistsError, ValueError, RuntimeError) as e:
        log.error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        log.critical(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
