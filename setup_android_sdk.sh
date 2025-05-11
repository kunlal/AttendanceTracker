#!/bin/bash

# Set up directories
SDK_DIR=$HOME/.buildozer/android/platform/android-sdk
mkdir -p "$SDK_DIR"

# Download and extract Android SDK command-line tools
cd "$SDK_DIR"
wget https://dl.google.com/android/repository/commandlinetools-linux-10406996_latest.zip -O cmdline-tools.zip
unzip cmdline-tools.zip -d temp

# Move command-line tools to correct location
mv temp/cmdline-tools "$SDK_DIR/cmdline-tools"

# Ensure the correct path for sdkmanager
export PATH="$SDK_DIR/cmdline-tools/bin:$PATH"

# Verify installation
if [ ! -f "$SDK_DIR/cmdline-tools/bin/sdkmanager" ]; then
    echo "Error: sdkmanager not found at expected location!"
    exit 1
fi

# Install Android SDK components
yes | "$SDK_DIR/cmdline-tools/bin/sdkmanager" --sdk_root="$SDK_DIR" \
  "platform-tools" "platforms;android-33" "build-tools;33.0.2"

echo "Android SDK setup complete!"

# Build APK using Buildozer
xvfb-run --auto-servernum --server-args='-screen 0 1024x768x24' buildozer android debug

