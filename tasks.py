"""
Parallax AI Development Tasks

Main task collection that imports all task modules.

Usage:
    inv --list                  # List all available commands
    inv --help <command>        # Get help for a specific command
    inv docker.up               # Start all services
    inv db.shell                # Connect to database
    inv dev.check               # Verify setup

See docs/DEVELOPER_COMMANDS.md for detailed documentation.
"""

from invoke import Collection

# Import task modules
from task_modules import docker, db, dev, backend, frontend

# Create namespace and add task modules
ns = Collection()
ns.add_collection(Collection.from_module(docker), name='docker')
ns.add_collection(Collection.from_module(db), name='db')
ns.add_collection(Collection.from_module(dev), name='dev')
ns.add_collection(Collection.from_module(backend), name='backend')
ns.add_collection(Collection.from_module(frontend), name='frontend')
