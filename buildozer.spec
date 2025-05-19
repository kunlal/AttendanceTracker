[app]
title = ChatGPT Kivy App
package.name = chatgpt_kivy
package.domain = org.chatgpt
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0

requirements = python3,kivy==2.3.1

orientation = portrait
fullscreen = 0
log_level = 2

android.api = 33
android.ndk = 25b
android.minapi = 21

# Use OpenGL ES2 for compatibility across devices
android.opengl = gles2

# Force software GL backend if GPU compatibility is an issue (optional fallback)
# Comment out by default unless you're hitting GL issues:
# environment variables set before Kivy loads
# p4a.environ = KIVY_GL_BACKEND=angle_sdl2

# Reduce unnecessary packaging issues
copy_to_apk = 1
