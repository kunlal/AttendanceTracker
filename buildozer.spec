[app]
title = ChatGPT Kivy App
package.name = chatgpt_kivy
package.domain = org.chatgpt
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0
requirements = python3==3.10.4,kivy==2.3.1
android.permissions = INTERNET
android.api = 29
android.ndk = 25b
android.arch = armeabi-v7a,arm64-v8a,x86,x86_64
