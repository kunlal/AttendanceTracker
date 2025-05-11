[app]

# Title of your app
title = Attendance Tracker

# Package name (name without spaces or special characters)
package.name = attendancetracker

# Package domain (reverse DNS format, change to your own domain)
package.domain = org.example

# Source directory
source.dir = .

# Files to include in the APK
source.include_exts = py,kv,jpg,png,json

# Main Python file
main.py = main.py

# Icon (optional)
# icon.filename = icon.png

# Supported orientation
orientation = portrait

# Fullscreen mode
fullscreen = 1

# Whether to hide the Android status bar
android.hide_statusbar = 0

# Application versioning
version = 1.0.0
package.version = 1.0

# Requirements: Kivy for GUI, Plyer for notifications
requirements = python3,kivy,plyer

# Permissions for notifications
android.permissions = RECEIVE_BOOT_COMPLETED

# Add required Android APIs
android.api = 33
android.build_tools = 33.0.2
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

# Architecture support
android.archs = arm64-v8a, armeabi-v7a

# Android entry point (keep this default)
entrypoint = org.kivy.android.PythonActivity

# Add static assets like the image and data file
android.add_assets = attendance.jpg, attendance_data.json

# Logging
log_level = 2

# Enable verbose output (for debugging)
verbose = 1

# Accept SDK license automatically
accept_sdk_license = True

# Directory for build artifacts
build_dir = .buildozer

[buildozer]

# Automatically install missing dependencies
# Set to 1 if you want Buildozer to install required packages automatically
requirement_install_recommendations = True

# Log everything for easier debugging
log_level = 2

# Save .apk to bin/ directory
output.bin_dir = bin
