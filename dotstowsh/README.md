# dotstow.sh - Dotfiles Management Script

A bash script to easily move configuration files to a GNU Stow-compatible dotfiles repository and automatically create symbolic links back to your home directory.

## Table of Contents

- [What is this?](#what-is-this)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Examples](#examples)
- [How it Works](#how-it-works)
- [Supported Applications](#supported-applications)
- [Directory Structure](#directory-structure)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

## What is this?

`dotstow.sh` simplifies the process of managing your dotfiles with GNU Stow. Instead of manually moving configuration files and setting up the correct directory structure, this script:

1. **Moves** your config files to a structured dotfiles repository
2. **Organizes** them by application name
3. **Creates symbolic links** back to their original locations using GNU Stow
4. **Handles** complex paths like `.config/app/config` automatically

## Prerequisites

- **Bash 3.2+** (works on macOS default bash and Linux)
- **GNU Stow** - Install with:
  - macOS: `brew install stow`
  - Ubuntu/Debian: `sudo apt install stow`
  - Arch Linux: `sudo pacman -S stow`
  - CentOS/RHEL: `sudo yum install stow`

## Installation

1. Download the script:

   ```bash
   curl -O https://raw.githubusercontent.com/kannansuresh/dotstow/main/dotstowsh/dotstow.sh
   # or download manually
   ```

2. Make it executable:

   ```bash
   chmod +x dotstow.sh
   ```

## Quick Start

### Basic Usage

```bash
# Move a config file to your dotfiles repo
./dotstow.sh ~/.zshrc

# Move a config directory
./dotstow.sh ~/.config/nvim
```

### With Custom Dotfiles Directory

```bash
# Specify your dotfiles directory
./dotstow.sh ~/.vimrc --dotfiles-dir ~/my-dotfiles
```

## Usage

```bash
./dotstow.sh <source_path> [app_name] [-d|--dotfiles-dir <path>] [-h|--help] [-v|--verbose]
```

### Parameters

- `<source_path>` (required): Path to the config file or directory to move
- `[app_name]` (optional): Custom application name (auto-detected if not provided)
- `-d, --dotfiles-dir <path>`: Specify dotfiles repository path
- `-h, --help`: Show help message
- `-v, --verbose`: Enable verbose output for debugging

### Interactive Prompts

The script will interactively ask you to:

1. **Confirm the dotfiles directory** (auto-detects if you're in a dotfiles repo)
2. **Review the move plan** before executing
3. **Choose whether to run stow** after moving files

## Examples

### Moving Shell Configuration

```bash
# Move .zshrc (will be organized under 'zsh' app)
./dotstow.sh ~/.zshrc

# Move .bashrc with custom dotfiles directory
./dotstow.sh ~/.bashrc --dotfiles-dir ~/dotfiles
```

### Moving Editor Configurations

```bash
# Move Neovim config (auto-detects as 'nvim')
./dotstow.sh ~/.config/nvim

# Move Vim config with custom app name
./dotstow.sh ~/.vimrc vim-config
```

### Moving Complex Configurations

```bash
# Move Alacritty terminal config
./dotstow.sh ~/.config/alacritty/alacritty.yml

# Move SSH config
./dotstow.sh ~/.ssh/config
```

### Running from Different Locations

```bash
# From anywhere, specifying dotfiles directory
cd ~/projects
./dotstow.sh ~/.gitconfig --dotfiles-dir ~/dotfiles

# From within your dotfiles directory (auto-detected)
cd ~/dotfiles
./dotstow.sh ~/.tmux.conf
```

## How it Works

### 1. Source Analysis

The script analyzes your source file/directory to:

- Determine the appropriate application name
- Calculate the target path in your dotfiles repository
- Validate that the source exists and is in your home directory

### 2. Application Name Detection

The script automatically detects application names using:

- **Filename mappings**: `.zshrc` → `zsh`, `.vimrc` → `vim`
- **.config path analysis**: `~/.config/nvim/` → `nvim`
- **Fallback logic**: Uses parent directory name

### 3. Directory Structure Creation

Creates a Stow-compatible structure:

```
dotfiles/
├── zsh/
│   └── .zshrc
├── nvim/
│   └── .config/
│       └── nvim/
│           ├── init.lua
│           └── lua/
└── git/
    └── .gitconfig
```

### 4. GNU Stow Integration

After moving files, optionally runs:

```bash
stow -d ~/dotfiles -t ~ <app_name>
```

This creates symbolic links from the repository back to your home directory.

## Supported Applications

The script includes built-in mappings for common applications:

### Shells

- `.zshrc`, `.bashrc`, `.bash_profile` → `bash`/`zsh`
- `config.fish` → `fish`
- `.kshrc`, `.cshrc` → `ksh`/`csh`

### Editors

- `.vimrc`, `.gvimrc` → `vim`/`gvim`
- `init.lua`, `init.vim` → `nvim`
- `.nanorc` → `nano`

### Development Tools

- `.gitconfig`, `.gitignore_global` → `git`
- `.npmrc` → `npm`
- `.pylintrc` → `pylint`

### Terminal Tools

- `.tmux.conf` → `tmux`
- `alacritty.yml` → `alacritty`
- `starship.toml` → `starship`

### System Tools

- `.Xresources`, `.xinitrc` → `xorg`
- `ssh/config` → `ssh`
- `config/i3/config` → `i3`

*See the script source for the complete list*

## Directory Structure

### Before (Traditional)

```
~/
├── .zshrc
├── .vimrc
├── .config/
│   ├── nvim/init.lua
│   └── alacritty/alacritty.yml
└── .gitconfig
```

### After (Stow-managed)

```
~/
├── .zshrc -> dotfiles/zsh/.zshrc
├── .vimrc -> dotfiles/vim/.vimrc
├── .config/
│   ├── nvim/ -> dotfiles/nvim/.config/nvim/
│   └── alacritty/ -> dotfiles/alacritty/.config/alacritty/
├── .gitconfig -> dotfiles/git/.gitconfig
└── dotfiles/
    ├── zsh/.zshrc
    ├── vim/.vimrc
    ├── nvim/.config/nvim/init.lua
    ├── alacritty/.config/alacritty/alacritty.yml
    └── git/.gitconfig
```

## Troubleshooting

### Common Issues

#### "declare: -A: invalid option"

- **Cause**: Old bash version (< 4.0)
- **Solution**: Use the compatible version of the script provided

#### "Directory ~/dotfiles doesn't exist" (but it does)

- **Cause**: Tilde expansion issue
- **Solution**: Use full path `/home/username/dotfiles` or the fixed script version

#### "realpath: command not found"

- **Cause**: Missing `realpath` utility (common on macOS)
- **Solution**: The script includes fallbacks to `readlink -f`

#### Stow conflicts

```
WARNING! stowing git would cause conflicts:
  * existing target is not owned by stow: .gitconfig
```

- **Cause**: File already exists in target location
- **Solution**: Remove the existing file first, or use `stow --adopt`

### Debug Mode

Run with verbose flag to see detailed execution:

```bash
./dotstow.sh ~/.zshrc -v
```

### Manual Stow Commands

If the automatic stow fails, you can run manually:

```bash
# Stow a specific app
stow -d ~/dotfiles -t ~ zsh

# Unstow (remove symlinks)
stow -d ~/dotfiles -t ~ -D zsh

# Restow (unstow then stow)
stow -d ~/dotfiles -t ~ -R zsh
```

## Advanced Usage

### Custom App Names

```bash
# Use a custom app name instead of auto-detection
./dotstow.sh ~/.config/myapp custom-app-name
```

### Multiple Configurations

```bash
# Move multiple configs for the same app
./dotstow.sh ~/.vimrc vim
./dotstow.sh ~/.vim vim  # Will be organized under the same 'vim' directory
```

### Batch Processing

```bash
#!/bin/bash
# Script to move all your configs at once
configs=(
    "~/.zshrc"
    "~/.config/nvim"
    "~/.gitconfig"
    "~/.tmux.conf"
)

for config in "${configs[@]}"; do
    ./dotstow.sh "$config" --dotfiles-dir ~/dotfiles
done
```

### Integration with Existing Dotfiles

If you already have a dotfiles repository:

1. Run from within your dotfiles directory for auto-detection
2. Or specify with `--dotfiles-dir`
3. The script will integrate with your existing structure

### Dotfiles Repository Auto-Detection

The script detects dotfiles repositories by checking for:

- Directory names: `dotfiles`, `configs`, `config`, `dotfiles.d`
- Marker files: `.stow-local-ignore`, `.stow-global-ignore`, `stow.sh`
- Multiple app directories (indicating a dotfiles structure)

## Best Practices

1. **Backup first**: Always backup your configs before running the script
2. **Test with non-critical files**: Try with less important configs first
3. **Use version control**: Keep your dotfiles repository in git
4. **Organize by application**: Let the script auto-detect app names for consistency
5. **Document your setup**: Keep notes about any manual configurations needed

## Contributing

Found a bug or want to add support for a new application?

- Check the `get_app_name_mapping()` function to add new file mappings
- Test with various bash versions
- Ensure compatibility with different operating systems

## License

This script is provided as-is under the MIT license. Use at your own risk and always backup your configuration files.
