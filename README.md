# Odoo Docker Builder

This repository contains modified Dockerfiles for all Odoo versions from 10.0 to 19.0. Each Dockerfile has been modified to download the necessary support files directly from GitHub during the build process, removing the need to have those files locally.

## Purpose

* Build Odoo Docker images using a single Dockerfile without additional files
* Especially helpful for users of Portainer, Portainer UI, or any container management UI that supports stack composition

## Benefits

* Simplifies deployment in UI-based container management systems
* Eliminates the need to download and manage multiple support files
* Works with all Odoo versions from 10.0 through 19.0
* Each version's Dockerfile is self-contained and standalone

## How to Use

1. Navigate to the folder of your desired Odoo version (e.g., `16.0`, `17.0`, `18.0`)
2. Copy the Dockerfile from that directory
3. Use it directly in your project or paste it into Portainer/UI composer
4. Build your Odoo container

### Building Specific Releases

You can build older releases of Odoo by modifying the `ODOO_RELEASE` variable in the Dockerfile:

1. Locate the `ENV ODOO_RELEASE=...` line in the Dockerfile
2. Change the version number to your desired release (e.g., `20250101` for a specific January 2025 release)
3. Build the container as usual

This allows you to deploy specific Odoo releases while maintaining the benefits of the standalone Dockerfile approach.

## Available Versions

- Odoo 10.0
- Odoo 11.0
- Odoo 12.0
- Odoo 13.0
- Odoo 14.0
- Odoo 15.0
- Odoo 16.0
- Odoo 17.0
- Odoo 18.0
- Odoo 19.0

## License

This project is licensed under the same terms as the original Odoo Docker files.