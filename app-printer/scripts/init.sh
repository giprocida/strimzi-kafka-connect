#!/usr/bin/env bash
# Commands to run when the container starts.

# Copy our custom .bashrc from /etc into the home directory.
# This container will typically run in Kubernetes with a PVC mounted
# on the home directory. That means our ~/.bashrc would be hidden
# under the mount.
# Any initialization commands you need
echo "Starting initialization..."

# Run the Python script
python3 /home/namespace_objects_printer.py

# Any other commands you need to run
echo "Initialization complete."

# This container is designed to run in Kubernetes, where it sleeps until it is needed.
exec sleep infinity
