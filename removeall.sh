#!/bin/bash
nvm deactivate
nvm uninstall <version>
rm -rf ~/.nvm

npm uninstall -g @vue/cli

apt purge python3.12-venv

