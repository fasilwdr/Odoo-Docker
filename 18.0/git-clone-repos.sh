#!/bin/bash
set -e

# This script clones Git repositories specified in GITPATH and updates odoo.conf
# It also installs Python packages from requirements.txt if present in the repository

# First argument should be GITPATH with comma-separated repository URLs
GITPATH="$1"
CONFIG_FILE="/etc/odoo/odoo.conf"
ADDON_PATH="/mnt/extra-addons"
REPOS=()

# Handle if no GITPATH is provided
if [ -z "$GITPATH" ]; then
    echo "No Git repositories specified, skipping clone operation."
    exit 0
fi

# Function to extract repository name from URL
get_repo_name() {
    local url="$1"
    # Extract repository name from URL (works for both HTTPS and SSH URLs)
    local repo_name=$(basename "$url" .git)
    echo "$repo_name"
}

# Function to install requirements.txt if it exists
install_requirements() {
    local repo_path="$1"
    local repo_name="$2"

    if [ -f "${repo_path}/requirements.txt" ]; then
        echo "Found requirements.txt in ${repo_name}, installing Python dependencies..."
        pip3 install -r "${repo_path}/requirements.txt"
        echo "Python dependencies for ${repo_name} installed successfully."
    else
        echo "No requirements.txt found in ${repo_name}, skipping dependency installation."
    fi
}

# Split repository URLs by comma
IFS=',' read -ra REPO_URLS <<< "$GITPATH"

echo "Starting to clone repositories..."

# Clone each repository into /mnt/extra-addons
for repo_url in "${REPO_URLS[@]}"; do
    # Trim leading/trailing whitespace
    repo_url=$(echo "$repo_url" | xargs)

    if [ -n "$repo_url" ]; then
        repo_name=$(get_repo_name "$repo_url")
        repo_path="${ADDON_PATH}/${repo_name}"
        echo "Cloning ${repo_name} from ${repo_url}"

        # Clone repository into /mnt/extra-addons
        cd "$ADDON_PATH"
        if [ ! -d "$repo_name" ]; then
            git clone "$repo_url" "$repo_name"
            echo "Successfully cloned ${repo_name}"
            # Install Python dependencies if requirements.txt exists
            install_requirements "$repo_path" "$repo_name"
            REPOS+=("$repo_name")
        else
            echo "Directory ${repo_name} already exists, updating repository"
            cd "$repo_name"
            git pull
            cd ..
            # Install Python dependencies in case requirements.txt was updated
            install_requirements "$repo_path" "$repo_name"
            REPOS+=("$repo_name")
        fi
    fi
done

echo "All repositories cloned successfully."