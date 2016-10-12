#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Main Digital Ocean Backing up script
# apt-get install python-requests

import os
import sys
import subprocess
import _config

# Uncomment to sync to use Digital Ocean block storage
#_config._lib.create_blockstorage()
#_config._lib.create_backups()
#_config._lib.delete_blockstorage()

# Uncomment to sync to use Digital Ocean temporary backup server
droplet = _config._lib.create_backup_server()
_config._lib.sync_backup_server(droplet)
_config._lib.delete_backup_server(str(droplet['id']))
