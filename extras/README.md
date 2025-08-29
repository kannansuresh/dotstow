# Dotfiles Management Scripts

A collection of bash scripts for managing dotfiles using GNU Stow with special support for macOS environments.

## Overview

This repository contains three main scripts that help you manage your dotfiles configuration:

- **`stow.sh`** - Sets up and links your dotfiles
- **`unstow.sh`** - Removes dotfiles symlinks
- **`migrate.sh`** - Safely moves your dotfiles to a new location

## Prerequisites

- **GNU Stow** must be installed on your system
- **Bash shell** (version 3.0 or higher)
- **macOS users**: Scripts include special handling for Nushell configuration

### Installing GNU Stow

**macOS (using Homebrew):**

```bash
brew install stow
```

**Ubuntu/Debian:**

```bash
sudo apt-get install stow
```

**Arch Linux:**

```bash
sudo pacman -S stow
```

## Repository Structure

Your dotfiles repository should be organized with each application's configuration in its own directory:

```
dotfiles/
├── stow.sh
├── unstow.sh
├── migrate.sh
├── vim/
│   └── .vimrc
├── zsh/
│   └── .zshrc
├── git/
│   └── .gitconfig
└── nushell/
    └── .config/
        └── nushell/
            ├── config.nu
            └── env.nu
```

## Script Usage

Ensure the scripts are executable:

```bash
chmod +x stow.sh unstow.sh migrate.sh
```

### 1. stow.sh - Link Your Dotfiles

**Basic usage:**

```bash
./stow.sh
```

Links all directories in your dotfiles repo to your home directory.

**Link only specific package:**

```bash
./stow.sh --only vim
```

Links only the specified package (e.g., vim configuration).

**What it does:**

- Creates `~/.config` directory on macOS if it doesn't exist
- Removes `.DS_Store` files automatically
- Creates symlinks for all configuration directories
- Special handling for Nushell on macOS (creates symlink in `~/Library/Application Support/`)

### 2. unstow.sh - Remove Dotfile Links

**Basic usage:**

```bash
./unstow.sh
```

Removes all symlinks created by stow from your home directory.

**Remove only specific package:**

```bash
./unstow.sh --only vim
```

Removes symlinks only for the specified package.

**What it does:**

- Removes `.DS_Store` files before processing
- Removes all symlinks created by stow
- Cleans up macOS-specific Nushell symlinks
- Leaves your original files untouched

### 3. migrate.sh - Move Dotfiles Repository

**Usage:**

```bash
./migrate.sh <old_directory> <new_directory>
```

**Example:**

```bash
./migrate.sh ~/old-dotfiles ~/Documents/dotfiles
```

**What it does:**

1. Shows a confirmation prompt with source and destination paths
2. Unstows all packages from the old location
3. Moves the entire repository to the new location
4. Re-stows all packages from the new location

**Safety features:**

- Requires explicit confirmation before proceeding
- Checks that source directory exists
- Prevents overwriting existing destination directories
- Atomic operation - either completes fully or fails safely

## Platform-Specific Features

### macOS Support

The scripts include special handling for macOS:

- **Nushell Configuration**: Creates a symlink from `~/.config/nushell` to `~/Library/Application Support/nushell` since Nushell looks for configs in the latter location on macOS
- **`.DS_Store` Cleanup**: Automatically removes macOS-generated `.DS_Store` files that can interfere with stow
- **Config Directory**: Ensures `~/.config` directory exists

## Common Workflows

### Initial Setup

```bash
# Clone your dotfiles repo
git clone <your-dotfiles-repo> ~/dotfiles
cd ~/dotfiles

# Link all your dotfiles
./stow.sh
```

### Adding New Configuration

```bash
# Create new package directory
mkdir ~/dotfiles/neovim
# Add your config files to the package
# Then link the new package
./stow.sh --only neovim
```

### Temporary Removal

```bash
# Remove all dotfiles temporarily
./unstow.sh

# Make system changes, then restore
./stow.sh
```

### Moving Repository Location

```bash
# Move from ~/dotfiles to ~/Documents/config/dotfiles
./migrate.sh ~/dotfiles ~/Documents/config/dotfiles
```

## Troubleshooting

### "Conflicts" Error

If stow reports conflicts, it means files already exist at the target location. Either:

1. Remove the conflicting files, or
2. Move them into your dotfiles repository structure

### Permission Denied

Ensure the scripts are executable:

```bash
chmod +x stow.sh unstow.sh migrate.sh
```

### Stow Command Not Found

Install GNU Stow using your system's package manager (see Prerequisites section).

### macOS Nushell Issues

If Nushell can't find its configuration on macOS, ensure:

1. The symlink exists: `ls -la "$HOME/Library/Application Support/nushell"`
2. The source directory exists: `ls -la ~/.config/nushell`

## Best Practices

1. **Test First**: Use `--only` flag to test individual packages before stowing everything
2. **Backup**: Keep your dotfiles in version control (Git)
3. **Clean Repository**: Don't commit `.DS_Store` files or other system-generated files
4. **Organize Logically**: Group related configurations (e.g., all shell configs in one package or separate them by shell)
5. **Document Changes**: Use commit messages to track what configurations you're changing

## Safety Notes

- The `migrate.sh` script moves your entire repository - ensure you have backups
- Always run `unstow.sh` before manually moving or deleting your dotfiles repository
- Test scripts in a safe environment before using on your primary system

## License

These scripts are provided as-is. Modify and use according to your needs.
