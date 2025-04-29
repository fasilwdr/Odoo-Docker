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

    # First, find all the COPY commands in the Dockerfile
    copy_commands = re.findall(r'COPY\s+[^\n]+', modified_content)

    # Process each file
    for filename, url in file_urls.items():
        if filename == "Dockerfile":
            continue  # Skip the Dockerfile itself

        # Try to find a COPY command that matches this filename
        matched = False
        for copy_cmd in copy_commands:
            # Check if this command is for our file
            if f"COPY {filename}" in copy_cmd or f"COPY ./{filename}" in copy_cmd:
                matched = True
                # Create replacement curl command
                if filename.endswith('.sh') or filename.endswith('.py'):
                    # For executable files
                    curl_cmd = f"RUN curl -sSL {url} -o /{filename} && chmod +x /{filename}"
                else:
                    # For regular files
                    curl_cmd = f"RUN curl -sSL {url} -o /{filename}"

                # Replace in the content, using a regex that matches the whole line
                pattern = re.escape(copy_cmd)
                modified_content = re.sub(pattern, curl_cmd, modified_content)
                break

        # Special case for wait-for-psql.py which might have a different destination path
        if not matched and filename == "wait-for-psql.py":
            pattern = re.compile(r'COPY\s+wait-for-psql.py\s+/usr/local/bin/wait-for-psql.py', re.IGNORECASE)
            if pattern.search(modified_content):
                curl_cmd = f"RUN curl -sSL {url} -o /usr/local/bin/wait-for-psql.py && chmod +x /usr/local/bin/wait-for-psql.py"
                modified_content = pattern.sub(curl_cmd, modified_content)
                matched = True

        # Special case for configuration files which might have a different destination path
        if not matched and filename == "odoo.conf":
            pattern = re.compile(r'COPY\s+odoo.conf\s+/etc/odoo/', re.IGNORECASE)
            if pattern.search(modified_content):
                curl_cmd = f"RUN curl -sSL {url} -o /etc/odoo/odoo.conf"
                modified_content = pattern.sub(curl_cmd, modified_content)
                matched = True

        if not matched:
            print(f"Warning: Could not find COPY command for {filename}")

    # Add all curl commands in a single RUN block at the end of the Dockerfile if any are missing
    missing_files = []
    for filename, url in file_urls.items():
        if filename == "Dockerfile":
            continue

        # Check if curl command for this file is already in the Dockerfile
        curl_pattern = f"curl -sSL {url}"
        if curl_pattern not in modified_content:
            missing_files.append((filename, url))

    if missing_files:
        print(f"Adding missing curl commands for: {', '.join(f[0] for f in missing_files)}")

        # Find appropriate location to add the commands (before USER odoo or at end)
        user_line_match = re.search(r'^USER\s+odoo\s*$', modified_content, re.MULTILINE)

        curl_block = "\n# Download any missing files\n"
        for filename, url in missing_files:
            if filename.endswith('.sh') or filename.endswith('.py'):
                if "wait-for-psql.py" in filename:
                    curl_block += f"RUN curl -sSL {url} -o /usr/local/bin/wait-for-psql.py && chmod +x /usr/local/bin/wait-for-psql.py\n"
                else:
                    curl_block += f"RUN curl -sSL {url} -o /{filename} && chmod +x /{filename}\n"
            elif "odoo.conf" in filename:
                curl_block += f"RUN curl -sSL {url} -o /etc/odoo/odoo.conf\n"
            else:
                curl_block += f"RUN curl -sSL {url} -o /{filename}\n"

        if user_line_match:
            # Insert before USER line
            pos = user_line_match.start()
            modified_content = modified_content[:pos] + curl_block + modified_content[pos:]
        else:
            # Append to end
            modified_content += curl_block

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