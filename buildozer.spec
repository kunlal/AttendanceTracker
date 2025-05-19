[app]
title = ChatGPT Kivy App
package.name = chatgpt_kivy
package.domain = org.chatgpt
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0

# ✅ Include all Python dependencies
requirements = python3,kivy==2.3.1,pytz,plyer

# ✅ Permissions if needed (optional for now)
# android.permissions = RECEIVE_BOOT_COMPLETED

# ✅ Ensure Android SDK versions are compatible
android.api = 33
android.minapi = 21
android.ndk = 25b

# ✅ Enable OpenGL ES2 (Kivy requires it)
android.opengl_es2 = 1

# ✅ Good defaults
log_level = 2
copy_to_apk = 1
orientation = portrait
fullscreen = 0

# (Optional) Icons and splash (if you want to customize app appearance later)
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/splash.png

# Leave bootstrap as default (SDL2 is default and required)
# android.bootstrap = sdl2

# Disable this to avoid issues unless you're packaging it for release
# android.release = False
