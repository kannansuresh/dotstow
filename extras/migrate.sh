#!/bin/bash
set -euo pipefail

# Check if the user provided old and new directories as arguments
if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <old_dotfiles_directory> <new_dotfiles_directory>"
  exit 1
fi

OLD_DIR="$1"
NEW_DIR="$2"
NEW_BASE="$(dirname "$NEW_DIR")"

# --- Add confirmation prompt here ---
echo "🚨 WARNING: This script will move your dotfiles from:"
echo "  $OLD_DIR"
echo "to:"
echo "  $NEW_DIR"
echo ""
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo "" # Add a newline for better formatting
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Migration canceled."
  exit 1
fi

# Check if the old directory exists
if [[ ! -d "$OLD_DIR" ]]; then
  echo "❌ Old dotfiles directory ($OLD_DIR) not found."
  exit 1
fi

# Check if the new directory already exists
if [[ -d "$NEW_DIR" ]]; then
  echo "❌ New dotfiles directory ($NEW_DIR) already exists. Please choose a different location or remove the existing one."
  exit 1
fi

echo "🔎 Unstowing from $OLD_DIR ..."
cd "$OLD_DIR"

# Unstow all top-level folders
for folder in */; do
  folder=${folder%/}
  echo "  ➖ Unstowing $folder"
  stow -D "$folder" --target="$HOME"
done

echo "📦 Moving repo to $NEW_DIR ..."
mkdir -p "$NEW_BASE"
mv "$OLD_DIR" "$NEW_DIR"

echo "🔗 Restowing from $NEW_DIR ..."
cd "$NEW_DIR"
for folder in */; do
  folder=${folder%/}
  echo "  ➕ Stowing $folder"
  stow "$folder" --target="$HOME"
done

echo "✅ Migration complete!"
echo "ℹ️ Your dotfiles are now managed from $NEW_DIR"