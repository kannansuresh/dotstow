# DotStow

A Python utility to streamline the process of moving configuration files into a GNU Stow-compatible dotfiles repository structure. DotStow intelligently organizes your dotfiles, handles the movement process, and optionally runs `stow` to create symbolic links.

## Features

- **Smart Detection**: Automatically detects dotfiles directories and infers application names
- **Safe Movement**: Validates paths and prevents overwriting existing files
- **GNU Stow Integration**: Optional automatic stowing after moving files
- **Cleanup**: Removes junk files like `.DS_Store` during the process
- **Interactive**: Provides confirmations and user-friendly prompts
- **Extensive Mapping**: Pre-configured mappings for 30+ common applications

## Installation

### Prerequisites

- Python 3.6+
- GNU Stow (optional, for symlinking functionality)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/kannansuresh/dotstow.git
cd dotstow

# Make executable
chmod +x dotstow.py

# Optional: Add to PATH for global usage
sudo ln -s $(pwd)/dotstow.py /usr/local/bin/dotstow
```

### Installing GNU Stow

**macOS (Homebrew):**
```bash
brew install stow
```

**Ubuntu/Debian:**
```bash
sudo apt install stow
```

**Arch Linux:**
```bash
sudo pacman -S stow
```

## Usage

### Basic Syntax

```bash
dotstow.py <source_path> [app_name] [options]
```

### Common Usage Patterns

#### 1. Move a config file with auto-detection
```bash
# DotStow will infer the app name and dotfiles directory
dotstow.py ~/.vimrc
```

#### 2. Specify custom app name
```bash
# Move .zshrc to a custom app directory named 'shell'
dotstow.py ~/.zshrc shell
```

#### 3. Use specific dotfiles directory
```bash
# Move to a specific dotfiles repository
dotstow.py ~/.config/nvim --dotfiles-dir ~/my-dotfiles
```

#### 4. Auto-stow after moving
```bash
# Move and automatically run stow without confirmation
dotstow.py ~/.gitconfig --auto-stow
```

#### 5. Skip stow entirely
```bash
# Just move files without any stow operations
dotstow.py ~/.tmux.conf --no-stow
```

## Examples

### Example 1: Moving Neovim Configuration

```bash
$ dotstow.py ~/.config/nvim

=== Dotfile Move ===
Source:      /home/user/.config/nvim
Target:      /home/user/dotfiles/nvim/.config/nvim
App name:    nvim
Dotfiles:    /home/user/dotfiles
Structure:   dotfiles/nvim/.config/nvim

Proceed with movement? [y/N]: y
Cleaning up junk files (.DS_Store)...
✓ Successfully moved to /home/user/dotfiles/nvim/.config/nvim
Run `stow` to symlink these files now? [y/N]: y
Running stow...
✓ Stow completed for 'nvim'
```

### Example 2: Setting up a new dotfiles repository

```bash
$ mkdir ~/my-dotfiles && cd ~/my-dotfiles
$ dotstow.py ~/.vimrc --dotfiles-dir ~/my-dotfiles

=== Dotfile Move ===
Source:      /home/user/.vimrc
Target:      /home/user/my-dotfiles/vim/.vimrc
App name:    vim
Dotfiles:    /home/user/my-dotfiles
Structure:   my-dotfiles/vim/.vimrc

Proceed with movement? [y/N]: y
```

### Example 3: Batch processing multiple configs

```bash
# Move multiple configurations
dotstow.py ~/.zshrc --auto-stow
dotstow.py ~/.gitconfig --auto-stow
dotstow.py ~/.tmux.conf --auto-stow
dotstow.py ~/.config/alacritty --auto-stow
```

## Supported Applications

DotStow includes built-in mappings for these common applications:

### Shells
- `zsh` (.zshrc)
- `bash` (.bashrc, .bash_profile, .bash_aliases)
- `fish` (config.fish)
- `ksh` (.kshrc)
- `csh` (.cshrc)

### Editors
- `vim` (.vimrc)
- `nvim` (init.lua, init.vim)
- `nano` (.nanorc)
- `vscode` (settings.json)
- `sublime-text` (preferences)

### Version Control
- `git` (.gitconfig, .gitignore_global)

### Terminal Tools
- `tmux` (.tmux.conf)
- `alacritty` (alacritty.yml, alacritty.toml)
- `kitty` (kitty.conf)
- `starship` (starship.toml)

### System Tools
- `ssh` (config)
- `gnupg` (gpg.conf)
- `htop` (htoprc)

...and many more! See the source code for the complete list.

## Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--dotfiles-dir` | `-d` | Specify dotfiles repository path |
| `--auto-stow` | | Run stow automatically without confirmation |
| `--no-stow` | | Skip stow operations entirely |
| `--verbose` | `-v` | Enable verbose output |
| `--help` | `-h` | Show help message |

## How It Works

### 1. Path Validation
- Ensures source path exists and is within the home directory
- Prevents moving files outside of safe locations

### 2. App Name Inference
- Uses built-in mappings to determine appropriate app names
- Falls back to filename-based inference for unknown files

### 3. Directory Structure
- Creates GNU Stow-compatible directory structure:
  ```
  dotfiles/
  ├── vim/
  │   └── .vimrc
  ├── nvim/
  │   └── .config/
  │       └── nvim/
  │           └── init.lua
  └── zsh/
      └── .zshrc
  ```

### 4. Safe Movement
- Checks for existing files to prevent overwrites
- Creates necessary parent directories
- Moves files atomically

### 5. Cleanup
- Removes macOS `.DS_Store` files
- Cleans up temporary artifacts

### 6. Stow Integration
- Optionally runs GNU Stow to create symbolic links
- Handles stow errors gracefully

## Directory Detection

DotStow can automatically detect dotfiles directories by looking for:

- Common names: `dotfiles`, `configs`, `config`, `dotfiles.d`
- Stow-specific files: `.stow-local-ignore`, `.stow-global-ignore`, `stow.sh`
- Multiple application directories from the known mappings

## Error Handling

DotStow provides clear error messages for common issues:

- **Source not found**: `Source path does not exist`
- **Outside home**: `Source must be within home directory`
- **Target exists**: `Target already exists: remove manually or choose different app name`
- **No stow**: `Stow is not installed or not found in PATH`

## Tips and Best Practices

### 1. Test First
Run DotStow with individual files to understand the behavior before batch processing.

### 2. Backup Important Configs
Always backup your configurations before moving them:
```bash
cp -r ~/.config/important-app ~/.config/important-app.backup
```

### 3. Use Version Control
Initialize your dotfiles directory as a git repository:
```bash
cd ~/dotfiles
git init
git add .
git commit -m "Initial dotfiles setup"
```

### 4. Custom App Names
For organization, you can group related configs:
```bash
dotstow.py ~/.bash_profile shell
dotstow.py ~/.zsh_aliases shell
```

### 5. Verify Stow Results
After stowing, verify that symbolic links were created correctly:
```bash
ls -la ~ | grep "^l"  # List symbolic links in home directory
```

## Troubleshooting

### Stow Conflicts
If stow reports conflicts, you may have existing files that need to be moved or removed:
```bash
# Remove conflicting files
rm ~/.existing-config
# Or move them to backup
mv ~/.existing-config ~/.existing-config.backup
```

### Permission Issues
Ensure you have write permissions to both source and destination directories:
```bash
ls -la ~/.config/
ls -la ~/dotfiles/
```

### Path Issues
Use absolute paths or ensure you're in the correct directory when running DotStow.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with a clear description

### Adding New Application Mappings

To add support for new applications, update the `APP_NAME_MAPPINGS` dictionary in the source code:

```python
APP_NAME_MAPPINGS = {
    # Add your mapping here
    ".myapprc": "myapp",
    ".config/myapp/config.toml": "myapp",
}
```

## License

This project is open source. See the repository for license details.

## Acknowledgments

- GNU Stow team for the excellent symlink management tool
- The dotfiles community for inspiration and best practices

---

**Repository**: [https://github.com/kannansuresh/dotstow](https://github.com/kannansuresh/dotstow)

For issues, feature requests, or contributions, please visit the GitHub repository.