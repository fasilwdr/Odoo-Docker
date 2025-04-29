#!/usr/bin/env python3
import json
import os
import requests
import re
from pathlib import Path


def fetch_file(url):
    """Fetch file content from URL"""
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch {url}: Status code {response.status_code}")
        return None


def process_dockerfile(dockerfile_content, file_urls):
    """
    Modify Dockerfile to use curl instead of COPY for the specified files
    """
    modified_content = dockerfile_content

    # Find and replace COPY commands with curl commands
    for filename, url in file_urls.items():
        if filename == "Dockerfile":
            continue  # Skip the Dockerfile itself

        # Different patterns for different files
        if filename.endswith('.sh'):
            # For shell scripts, we need to make them executable
            copy_pattern = re.compile(rf'COPY\s+{filename}\s+/.*?(?:\n|$)', re.IGNORECASE | re.MULTILINE)
            curl_command = f'RUN curl -sSL {url} -o /{filename} && chmod +x /{filename}\n'
        elif filename.endswith('.py'):
            # For Python scripts
            copy_pattern = re.compile(rf'COPY\s+{filename}\s+/.*?(?:\n|$)', re.IGNORECASE | re.MULTILINE)
            curl_command = f'RUN curl -sSL {url} -o /{filename} && chmod +x /{filename}\n'
        else:
            # For config files
            copy_pattern = re.compile(rf'COPY\s+{filename}\s+/.*?(?:\n|$)', re.IGNORECASE | re.MULTILINE)
            curl_command = f'RUN curl -sSL {url} -o /{filename}\n'

        # Replace COPY with curl
        if copy_pattern.search(modified_content):
            modified_content = copy_pattern.sub(curl_command, modified_content)
        else:
            print(f"Warning: Could not find COPY command for {filename}")

    return modified_content


def main():
    # Load data.json
    with open('data.json', 'r') as f:
        data = json.load(f)

    # Process each version
    for version, file_urls in data.items():
        print(f"Processing version {version}...")

        # Create directory if it doesn't exist
        os.makedirs(version, exist_ok=True)

        # Fetch and process the Dockerfile
        dockerfile_url = file_urls.get('Dockerfile')
        if not dockerfile_url:
            print(f"Error: No Dockerfile URL for version {version}")
            continue

        # Fetch original Dockerfile
        dockerfile_content = fetch_file(dockerfile_url)
        if not dockerfile_content:
            print(f"Error: Could not fetch Dockerfile for version {version}")
            continue

        # Modify the Dockerfile
        modified_dockerfile = process_dockerfile(dockerfile_content, file_urls)

        # Save the modified Dockerfile
        with open(os.path.join(version, 'Dockerfile'), 'w') as f:
            f.write(modified_dockerfile)

        print(f"Updated Dockerfile for version {version}")

    print("All Dockerfiles have been updated.")


if __name__ == "__main__":
    main()