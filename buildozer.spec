[app]
title = YourKivyApp
package.name = yourkivyapp
package.domain = org.yourdomain
source.dir = .
source.include_exts = py,json
version = 1.0
requirements = python3,kivy==2.3.1,json,calendar,datetime
arch = armeabi-v7a,x86
orientation = portrait
fullscreen = 1
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 23b
android.gradle_dependencies = androidx.appcompat:appcompat:1.2.0

[buildozer]
log_level = 2
warn_on_root = 1
