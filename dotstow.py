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


class DotfileMover:
    """Handles the moving of dotfiles to a Stow-compatible repository."""

    APP_NAME_MAPPINGS = {
        # Shells
        ".zshrc": "zsh",
        ".bashrc": "bash",
        ".bash_profile": "bash",
        ".bash_aliases": "bash",
        ".profile": "shell",
        ".login": "shell",
        ".kshrc": "ksh",
        ".cshrc": "csh",
        "config.fish": "fish",
        # Editors
        ".vimrc": "vim",
        ".gvimrc": "gvim",
        "init.lua": "nvim",
        "init.vim": "nvim",
        ".ideavimrc": "ideavim",
        ".nanorc": "nano",
        # Git
        ".gitconfig": "git",
        ".gitignore_global": "git",
        ".git-templates": "git",
        ".gitattributes_global": "git",
        ".config/git/ignore": "git",
        # Terminal Multiplexers
        ".tmux.conf": "tmux",
        ".screenrc": "screen",
        # Terminal Emulators
        "alacritty.yml": "alacritty",
        "alacritty.toml": "alacritty",
        ".config/kitty/kitty.conf": "kitty",
        # Window Managers & Desktop Environment
        ".xprofile": "xorg",
        ".Xresources": "xorg",
        ".Xmodmap": "xorg",
        ".xinitrc": "xorg",
        ".config/i3/config": "i3",
        ".config/polybar/config.ini": "polybar",
        # Other Common Applications
        "starship.toml": "starship",
        "direnvrc": "direnv",
        ".ssh/config": "ssh",
        ".gnupg/gpg.conf": "gnupg",
        ".pylintrc": "pylint",
        ".config/htop/htoprc": "htop",
        ".npmrc": "npm",
        ".gemrc": "gem",
        ".inputrc": "readline",
        # Editor-specific configurations within .config
        ".config/Code/User/settings.json": "vscode",
        ".config/sublime-text/Packages/User/Preferences.sublime-settings": "sublime-text",
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
        self.dotfiles_dir = self._get_dotfiles_dir(dotfiles_dir)
        self.auto_stow = auto_stow
        self.no_stow = no_stow

    def _get_dotfiles_dir(self, dotfiles_dir: Optional[str]) -> Path:
        """Get the dotfiles directory, with smart defaults."""
        if dotfiles_dir:
            path = Path(dotfiles_dir).expanduser().resolve()
            if not path.exists():
                raise ValueError(f"Specified dotfiles directory does not exist: {path}")
            return path

        current_dir = Path.cwd()
        if self._is_dotfiles_directory(current_dir):
            print(f"Detected dotfiles directory: {current_dir}")
            try:
                confirm = (
                    input("Use current directory as dotfiles repo? [Y/n]: ")
                    .strip()
                    .lower()
                )
                if confirm in ("", "y", "yes"):
                    return current_dir
            except (KeyboardInterrupt, EOFError):
                print("\nOperation cancelled.")
                sys.exit(0)

        default_path = Path.home() / "dotfiles"
        try:
            print(f"Current directory: {current_dir}")
            user_input = input(
                f"Enter dotfiles directory path (default: {default_path}): "
            ).strip()
            path = Path(user_input or str(default_path)).expanduser().resolve()

            if not path.exists():
                create = (
                    input(f"Directory {path} doesn't exist. Create it? [y/N]: ")
                    .strip()
                    .lower()
                )
                if create in ("y", "yes"):
                    path.mkdir(parents=True, exist_ok=True)
                    print(f"Created dotfiles directory: {path}")
                else:
                    raise ValueError("Dotfiles directory is required")

            return path
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            sys.exit(0)

    def _is_dotfiles_directory(self, path: Path) -> bool:
        """Check if a directory looks like a dotfiles repository."""
        common_dotfile_names = ["dotfiles", "configs", "config", "dotfiles.d"]
        if path.name.lower() in common_dotfile_names:
            return True

        if (
            (path / ".stow-local-ignore").exists()
            or (path / ".stow-global-ignore").exists()
            or (path / "stow.sh").exists()
        ):
            return True

        app_dirs = [
            d
            for d in path.iterdir()
            if d.is_dir() and d.name in self.APP_NAME_MAPPINGS.values()
        ]
        return len(app_dirs) >= 2

    def _infer_app_name(self) -> str:
        """Infer application name from source path."""
        base_name = self.source_path.name.lstrip(".")
        if base_name in self.APP_NAME_MAPPINGS:
            return self.APP_NAME_MAPPINGS[base_name]

        if base_name == "config":
            parent_name = self.source_path.parent.name
            if parent_name == ".config":
                return self.source_path.parent.parent.name
            return parent_name

        return base_name

    def _validate_source(self) -> None:
        """Validate the source path exists and is within home directory."""
        if not self.source_path.exists():
            raise ValueError(f"Source path does not exist: {self.source_path}")

        try:
            self.source_path.relative_to(Path.home())
        except ValueError:
            raise ValueError(
                f"Source must be within home directory: {self.source_path}"
            )

    def _calculate_target_path(self, app_name: str) -> Path:
        """Calculate the target path in the dotfiles repository."""
        home = Path.home()
        relative_path = self.source_path.relative_to(home)
        if relative_path.parts[0] == ".config":
            config_subpath = relative_path.relative_to(".config")
            return self.dotfiles_dir / app_name / ".config" / config_subpath
        return self.dotfiles_dir / app_name / relative_path

    def _check_target_exists(self, target_path: Path) -> None:
        """Check if target already exists to prevent overwrites."""
        if target_path.exists():
            raise FileExistsError(
                f"Target already exists: {target_path}\n"
                "Remove it manually or choose a different app name."
            )

    def _perform_movement(self, target_path: Path) -> None:
        """Execute the actual file/directory move operation."""
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(self.source_path), str(target_path))
        except Exception as e:
            raise RuntimeError(f"Failed to move files: {e}")

    def _run_stow(self, app_name: str) -> None:
        """Run stow to symlink the app."""
        try:
            subprocess.run(
                [
                    "stow",
                    "-d",
                    str(self.dotfiles_dir),
                    "-t",
                    str(Path.home()),
                    app_name,
                ],
                check=True,
            )
            print(f"✓ Stow completed for '{app_name}'")
        except FileNotFoundError:
            print(
                "Stow is not installed or not found in PATH. Please install GNU Stow."
            )
        except subprocess.CalledProcessError as e:
            print(f"Stow failed: {e}")

    def move(self) -> None:
        """Execute the complete move process with confirmations and stow."""
        self._validate_source()

        try:
            self.source_path.relative_to(self.dotfiles_dir)
            print("The source path is already within the specified dotfiles directory.")
            print("No movement is needed. You may proceed with `stow`.")
            app_name = self.app_name or self._infer_app_name()
            print(f"\nExample command: `cd {self.dotfiles_dir} && stow {app_name}`")
            return
        except ValueError:
            pass

        app_name = self.app_name or self._infer_app_name()
        target_path = self._calculate_target_path(app_name)
        self._check_target_exists(target_path)

        print("=== Dotfile Move ===")
        print(f"Source:      {self.source_path}")
        print(f"Target:      {target_path}")
        print(f"App name:    {app_name}")
        print(f"Dotfiles:    {self.dotfiles_dir}")
        try:
            rel_target = target_path.relative_to(self.dotfiles_dir)
            print(f"Structure:   {self.dotfiles_dir.name}/{rel_target}")
        except ValueError:
            pass
        print()

        # Confirm move
        try:
            confirm = input("Proceed with movement? [y/N]: ").strip().lower()
            if confirm not in ("y", "yes"):
                print("Movement cancelled.")
                return
        except (KeyboardInterrupt, EOFError):
            print("\nMovement cancelled.")
            return

        self._perform_movement(target_path)

        # Cleanup junk files
        print("Cleaning up junk files (.DS_Store)...")
        subprocess.run(
            ["find", str(target_path), "-name", ".DS_Store", "-delete"], check=False
        )

        print(f"✓ Successfully moved to {target_path}")

        # Handle stow logic
        if self.no_stow:
            print("Stow skipped due to --no-stow flag.")
        elif self.auto_stow:
            print("Running stow automatically due to --auto-stow flag...")
            self._run_stow(app_name)
        else:
            try:
                confirm_stow = (
                    input("Run `stow` to symlink these files now? [y/N]: ")
                    .strip()
                    .lower()
                )
                if confirm_stow in ("y", "yes"):
                    print("Running stow...")
                    self._run_stow(app_name)
                else:
                    print("Stow skipped. You can run it manually later.")
            except (KeyboardInterrupt, EOFError):
                print("\nStow cancelled.")


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Move configuration files to GNU Stow-compatible dotfiles repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ~/.config/nvim --dotfiles-dir ~/my-dotfiles
  cd ~/dotfiles && %(prog)s ~/.zshrc
  %(prog)s ~/.gitconfig git
  %(prog)s ~/.vimrc --dotfiles-dir ~/new-dotfiles
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
        help="Run stow automatically without confirmation",
    )
    parser.add_argument(
        "--no-stow", action="store_true", help="Skip running stow completely"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    return parser


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    try:
        mover = DotfileMover(
            source_path=args.source_path,
            app_name=args.app_name,
            dotfiles_dir=args.dotfiles_dir,
            auto_stow=args.auto_stow,
            no_stow=args.no_stow,
        )
        mover.move()
    except (ValueError, FileExistsError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
