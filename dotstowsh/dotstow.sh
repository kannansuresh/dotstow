#!/bin/bash

set -euo pipefail

# --- Helper Functions ---

# Function to get app name mapping - compatible with older bash versions
get_app_name_mapping() {
    local key="$1"
    case "$key" in
        # Shells
        ".zshrc") echo "zsh" ;;
        ".bashrc") echo "bash" ;;
        ".bash_profile") echo "bash" ;;
        ".bash_aliases") echo "bash" ;;
        ".profile") echo "shell" ;;
        ".login") echo "shell" ;;
        ".kshrc") echo "ksh" ;;
        ".cshrc") echo "csh" ;;
        "config.fish") echo "fish" ;;
        # Editors
        ".vimrc") echo "vim" ;;
        ".gvimrc") echo "gvim" ;;
        "init.lua") echo "nvim" ;;
        "init.vim") echo "nvim" ;;
        ".ideavimrc") echo "ideavim" ;;
        ".nanorc") echo "nano" ;;
        # Git
        ".gitconfig") echo "git" ;;
        ".gitignore_global") echo "git" ;;
        ".git-templates") echo "git" ;;
        ".gitattributes_global") echo "git" ;;
        "config/git/ignore") echo "git" ;;
        # Terminal Multiplexers
        ".tmux.conf") echo "tmux" ;;
        ".screenrc") echo "screen" ;;
        # Terminal Emulators
        "alacritty.yml") echo "alacritty" ;;
        "alacritty.toml") echo "alacritty" ;;
        "config/kitty/kitty.conf") echo "kitty" ;;
        # Window Managers & Desktop Environment
        ".xprofile") echo "xorg" ;;
        ".Xresources") echo "xorg" ;;
        ".Xmodmap") echo "xorg" ;;
        ".xinitrc") echo "xorg" ;;
        "config/i3/config") echo "i3" ;;
        "config/polybar/config.ini") echo "polybar" ;;
        # Other Common Applications
        "starship.toml") echo "starship" ;;
        "direnvrc") echo "direnv" ;;
        "ssh/config") echo "ssh" ;;
        "gnupg/gpg.conf") echo "gnupg" ;;
        ".pylintrc") echo "pylint" ;;
        "config/htop/htoprc") echo "htop" ;;
        ".npmrc") echo "npm" ;;
        ".gemrc") echo "gem" ;;
        ".inputrc") echo "readline" ;;
        # Editor-specific configurations within .config
        "config/Code/User/settings.json") echo "vscode" ;;
        "config/sublime-text/Packages/User/Preferences.sublime-settings") echo "sublime-text" ;;
        # Ghostty
        "config/ghostty/config") echo "ghostty" ;;
        # Default case
        *) echo "" ;;
    esac
}

# Function to check if mapping exists
has_app_name_mapping() {
    local key="$1"
    local result=$(get_app_name_mapping "$key")
    [[ -n "$result" ]]
}

# Function to display usage and examples
usage() {
    cat << EOF
Move configuration files to GNU Stow-compatible dotfiles repository

Usage: $0 <source_path> [app_name] [-d|--dotfiles-dir <path>]

Examples:
  # Run from anywhere, specify dotfiles directory
  $0 ~/.config/nvim --dotfiles-dir ~/my-dotfiles

  # Run from within your dotfiles directory (auto-detected)
  cd ~/dotfiles && $0 ~/.zshrc

  # Specify custom app name
  $0 ~/.gitconfig git

  # Create dotfiles directory if it doesn't exist
  $0 ~/.vimrc --dotfiles-dir ~/new-dotfiles
EOF
    exit 1
}

# Function to check if a directory looks like a dotfiles repository
is_dotfiles_directory() {
    local path="$1"
    # Check common names
    [[ "$(basename "$path" | tr '[:upper:]' '[:lower:]')" =~ ^(dotfiles|configs|config|dotfiles\.d)$ ]] && return 0
    # Check for marker files
    [[ -f "$path/.stow-local-ignore" || -f "$path/.stow-global-ignore" || -f "$path/stow.sh" ]] && return 0
    # Check for multiple known app directories (simplified check)
    local app_count=0
    for dir in vim nvim git bash zsh tmux; do
        if [[ -d "$path/$dir" ]]; then
            ((app_count++))
        fi
    done
    [[ "$app_count" -ge 2 ]] && return 0

    return 1
}

# Function to get the dotfiles directory
get_dotfiles_dir() {
    local default_dir="$HOME/dotfiles"
    local dir_input="$1"
    local dotfiles_dir=""

    if [[ -n "$dir_input" ]]; then
        # Expand tilde manually if present
        dir_input_expanded="${dir_input/#\~/$HOME}"
        dotfiles_dir="$(realpath -m "$dir_input_expanded" 2>/dev/null || readlink -f "$dir_input_expanded" 2>/dev/null || echo "$dir_input_expanded")"
        if [[ ! -d "$dotfiles_dir" ]]; then
            echo "Error: Specified dotfiles directory does not exist: $dotfiles_dir" >&2
            exit 1
        fi
        echo "$dotfiles_dir"
        return
    fi

    # Check for auto-detection
    if is_dotfiles_directory "$PWD"; then
        echo "Detected dotfiles directory: $PWD" >&2
        read -rp "Use current directory as dotfiles repo? [Y/n]: " confirm
        confirm=${confirm:-y}
        if [[ "$confirm" =~ ^[Yy]$ ]]; then
            echo "$PWD"
            return
        fi
    fi

    # Interactive prompt as fallback
    echo "Current directory: $PWD" >&2
    read -rp "Enter dotfiles directory path (default: $default_dir): " user_input
    # Expand tilde manually if present
    user_input_expanded="${user_input/#\~/$HOME}"
    dotfiles_dir="$(realpath -m "${user_input_expanded:-$default_dir}" 2>/dev/null || readlink -f "${user_input_expanded:-$default_dir}" 2>/dev/null || echo "${user_input_expanded:-$default_dir}")"

    if [[ ! -d "$dotfiles_dir" ]]; then
        read -rp "Directory $dotfiles_dir doesn't exist. Create it? [y/N]: " create
        create=${create:-n}
        if [[ "$create" =~ ^[Yy]$ ]]; then
            mkdir -p "$dotfiles_dir"
            echo "Created dotfiles directory: $dotfiles_dir" >&2
        else
            echo "Error: Dotfiles directory is required" >&2
            exit 1
        fi
    fi
    echo "$dotfiles_dir"
}

# Function to infer the application name
infer_app_name() {
    local source_path="$1"
    local base_name="$(basename "$source_path" | sed 's/^\.//')"

    # Check special mappings first
    if has_app_name_mapping "$base_name"; then
        get_app_name_mapping "$base_name"
        return
    fi

    # Handle paths relative to .config
    local relative_to_home="${source_path#$HOME/}"
    if [[ "$relative_to_home" == ".config/"* ]]; then
        local config_path="${relative_to_home#".config/"}"
        local first_part="${config_path%%/*}"
        if has_app_name_mapping "config/$first_part/$first_part.conf" || has_app_name_mapping "config/$first_part/config"; then
            echo "$first_part"
            return
        fi
        # For .config paths, use the first directory name
        echo "$first_part"
        return
    fi

    # Fallback: check parent directory name
    local parent_dir="$(basename "$(dirname "$source_path")")"
    if [[ "$parent_dir" == ".config" ]]; then
        parent_dir="$(basename "$(dirname "$(dirname "$source_path")")")"
    fi
    echo "$parent_dir"
}

# Function to clean up junk files
cleanup_junk() {
    echo "Cleaning up junk files..."
    find "$1" -name ".DS_Store" -delete 2>/dev/null || true
    echo "Junk file cleanup complete."
}

# --- Main Script Logic ---
source_path_input=""
app_name_input=""
dotfiles_dir_input=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -d|--dotfiles-dir)
            dotfiles_dir_input="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        -v|--verbose)
            set -x
            shift
            ;;
        *)
            if [[ -z "$source_path_input" ]]; then
                source_path_input="$1"
                shift
            elif [[ -z "$app_name_input" ]]; then
                app_name_input="$1"
                shift
            else
                echo "Error: Too many arguments." >&2
                usage
            fi
            ;;
    esac
done

# Validate required arguments
if [[ -z "$source_path_input" ]]; then
    echo "Error: A source path is required." >&2
    usage
fi

# Expand tilde in source path if present
source_path_expanded="${source_path_input/#\~/$HOME}"
source_path="$(realpath -m "$source_path_expanded" 2>/dev/null || readlink -f "$source_path_expanded" 2>/dev/null || echo "$source_path_expanded")"

# Validate source path
if [[ ! -e "$source_path" ]]; then
    echo "Error: Source path does not exist: $source_path" >&2
    exit 1
fi
if [[ "$source_path" != "$HOME"* ]]; then
    echo "Error: Source must be within home directory: $source_path" >&2
    exit 1
fi

# Determine dotfiles directory
dotfiles_dir=$(get_dotfiles_dir "$dotfiles_dir_input")
echo "Using dotfiles directory: $dotfiles_dir"

# Determine app name
app_name="${app_name_input:-$(infer_app_name "$source_path")}"

# Calculate target path
relative_path="${source_path#$HOME/}"
if [[ "$relative_path" == .config/* ]]; then
    target_path="$dotfiles_dir/$app_name/$relative_path"
else
    target_path="$dotfiles_dir/$app_name/$relative_path"
fi

# Pre-move checks
if [[ -e "$target_path" ]]; then
    echo "Error: Target already exists: $target_path" >&2
    echo "Remove it manually or choose a different app name." >&2
    exit 1
fi

# --- First Confirmation (Movement) ---
echo -e "\n=== Dotfile Move Plan ==="
echo "Source:      $source_path"
echo "Target:      $target_path"
echo "App name:    $app_name"
echo "Dotfiles:    $dotfiles_dir"
echo "Structure:   $(basename "$dotfiles_dir")/${target_path#$dotfiles_dir/}"

read -rp "Proceed with moving the file? [y/N]: " confirm_move
confirm_move=${confirm_move:-n}
if [[ ! "$confirm_move" =~ ^[Yy]$ ]]; then
    echo "Movement cancelled."
    exit 0
fi

# Execute movement
if ! mkdir -p "$(dirname "$target_path")"; then
    echo "Error: Failed to create target directory." >&2
    exit 1
fi
if ! mv "$source_path" "$target_path"; then
    echo "Error: Failed to move files." >&2
    exit 1
fi

echo "✓ Successfully moved to $target_path"

# Cleanup junk files after moving the source
cleanup_junk "$dotfiles_dir"

# --- Second Confirmation (Stowing) ---
echo -e "\n=== Next Steps: Stowing ==="
echo "The file has been moved to your dotfiles repository."
echo "Now, you can create a symbolic link from the repository back to your home directory."

read -rp "Would you like to run the 'stow' command now? [y/N]: " confirm_stow
confirm_stow=${confirm_stow:-n}
if [[ "$confirm_stow" =~ ^[Yy]$ ]]; then
    echo "Running: stow -d $dotfiles_dir -t ~ $app_name"
    if ! stow -d "$dotfiles_dir" -t ~ "$app_name"; then
        echo "Error: 'stow' failed. Please check the output above." >&2
        exit 1
    fi
    echo "✓ 'stow' command executed successfully."
else
    echo "Skipping 'stow' command."
    echo -e "\nTo symlink the dotfiles later, run this command:"
    echo "  stow -d $dotfiles_dir -t ~ $app_name"
fi