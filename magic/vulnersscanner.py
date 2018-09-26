#!/usr/bin/python
# -*- coding: utf-8 -*-


# *****************************************************VULNERS**************************************************
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
try:
    from subprocess import DEVNULL # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')

import json
from isocompare2 import accessIso

# def sshCommand(cmd):
#     cmdResult = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=DEVNULL, shell=True).communicate()[0]
#     if isinstance(cmdResult, bytes):
#         cmdResult = cmdResult.decode('utf8')
#     return cmdResult
#
# cmd = "rpm -qa"
# sshCommand(cmd).splitlines() if cmd else None

# парсит cvssvector
def parseCvssVector(cvssVector=None):
    cvssVectorLst = cvssVector.rstrip('/').split('/')
    res = {}
    for i in cvssVectorLst:
        if i[0:3] == 'AV:':
            res.update(dict(AV=i[3:len(i)]))
        if i[0:3] == 'AC:':
            res.update(dict(AC=i[3:len(i)]))
        if i[0:3] == 'Au:':
            res.update(dict(Au=i[3:len(i)]))
        if i[0:2] == 'C:':
            res.update(dict(C=i[2:len(i)]))
        if i[0:2] == 'I:':
            res.update(dict(I=i[2:len(i)]))
        if i[0:2] == 'A:':
            res.update(dict(A=i[2:len(i)]))
    return res


# посылаем список пакетов и получаем результат сканирования
def requestForVulners(pkgs=[]):
    VULNERS_LINKS = {'pkgChecker': 'https://vulners.com/api/v3/audit/audit/',
                     'bulletin': 'https://vulners.com/api/v3/search/id/?id=%s'}

    payload = {'os': 'redhat', 'version': '7', 'package': pkgs}

    req = urllib2.Request(VULNERS_LINKS.get('pkgChecker'))
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req, json.dumps(payload).encode('utf-8'))

    responseData = response.read()
    if isinstance(responseData, bytes):
        responseData = responseData.decode('utf8')
    responseData = json.loads(responseData)
    resultCode = responseData.get("result")

    if resultCode == "OK":
        # print(json.dumps(responseData, indent=4))
        if len(responseData['data']['packages']) != 0:
            result = []
            for pkg in pkgs:
                try:
                    pkgsRes = responseData['data']['packages'][pkg]
                    bulletin = []
                    for key in pkgsRes:
                        bulletin.append(dict(id=key, pkg=pkgsRes[key][0]['bulletinPackage'],
                                         cveList=pkgsRes[key][0]['cvelist'],
                                         # cvssScore="%g" % pkgsRes[key][0]['cvss']['score'],
                                         cvssScore=pkgsRes[key][0]['cvss']['score'],
                                         cvssVector=parseCvssVector(pkgsRes[key][0]['cvss']['vector'])))

                    maxScore = None
                    maxAC = None
                    for i in bulletin:
                        if i['cvssScore'] > maxScore:
                            maxScore = i['cvssScore']
                            if i['cvssVector'] != {}:
                                maxAC = i['cvssVector']['AC']

                    result.append(dict(pkgName=pkg, maxScore=maxScore, maxAC=maxAC,
                                       bulletin=sorted(bulletin, key=lambda x: x['cvssScore'], reverse=True)))
                except:
                    pass

            return sorted(result, key=lambda x: x['pkgName'])

        else:
            return 'ok'

    else:
        raise Exception("Error - %s" % responseData.get('data').get('error'))


def runScanner(isoPath=None, pkgsName=[], pkgsNVRA=[]):
    pkgs = []
    # сканирует пакеты на образе
    if not pkgsName and not pkgsNVRA:
        iso = accessIso(isoPath)
        pkgsOnIso = iso.getPkgLst()
        del iso

        pkgs = [pkg['nvra'] for pkg in pkgsOnIso]

    # сканирует пакеты на образе по списку
    elif pkgsName and not pkgsNVRA:
        iso = accessIso(isoPath)
        pkgsOnIso = iso.getPkgLst()
        del iso

        pkgs = [pkg['nvra'] for pkg in pkgsOnIso if pkg['name'] in pkgsName]

    # сканирует список пакетов
    elif not pkgsName and pkgsNVRA:
        pkgs = pkgsNVRA

    if not pkgs:
        return 'no data'

    return requestForVulners(pkgs)


# iso = '/mnt/pub/Temp/GosLinux/17.04.2018/goslinux-7.1-20180417.0-Everything-x86_64-DVD1.iso'
# pkgsName = ['ghostscript-cups', 'openssh']
# pkgsName = ['firefox']
# pkgsNVRA = ['openssl-1.0.2e-5.el7.x86_64', 'gnome-shell-3.14.4-54.el7.x86_64']
# pkgs = ['graphite2-1.3.6-1.el7.x86_64', 'openssh-7.4p1-13.el7.x86_64', 'java-1.7.0-openjdk-headless-1.7.0.121-2.6.8.0.el7.x86_64']
# pkgs = ['gnome-shell-3.14.4-54.el7.x86_64']


# print(runScanner(isoPath=iso, pkgsName=[], pkgsNVRA=[]))
# print(runScanner(isoPath=iso, pkgsName=pkgsName, pkgsNVRA=[]))
# print(runScanner(isoPath=iso, pkgsName=[], pkgsNVRA=pkgsNVRA))

# список обьектов оценки
# f = open('123.txt', 'r')
# res = []
# for line in f:
#     ind = line.rfind('-')
#     line = line[0:ind]
#     ind = line.rfind('-')
#     line = line[0:ind]
#     # print(line)
#     res.append(line)
#
# res.sort()
# print(res)

