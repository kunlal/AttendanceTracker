[app]
title = ChatGPT Kivy App
package.name = chatgpt_kivy
package.domain = org.chatgpt
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0

requirements = python3,kivy==2.3.1

# (No permissions needed, since your app doesn't require any)
# android.permissions = 

# Supported Android API/NDK versions
android.api = 33
android.ndk = 23b

# Supported architectures (Buildozer now handles this automatically)
# android.arch is deprecated — no need to include

# Ensure log output for debugging
log_level = 2

# Include source files in the APK
copy_to_apk = 1

# Optionally include this if you use .kv or assets
# (already covered by source.include_exts)

# Build config
orientation = portrait
fullscreen = 0
