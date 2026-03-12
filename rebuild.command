#!/bin/bash
cd "$(dirname "$0")"
rm -rf dist build
pyinstaller --name "Budget Tracker" --windowed --onedir main.py
echo "Done! App is in dist/"
