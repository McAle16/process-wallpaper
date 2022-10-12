#!/bin/bash

echo "Creating process wallpaper..."

top -b -n 1 > top.out
nice python3 generateWallpaper.py

echo "Done! Enjoy your brand-new desktop"
