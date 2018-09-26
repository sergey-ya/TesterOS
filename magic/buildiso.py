#!/usr/bin/python
# coding: utf_8


import os, subprocess
from magic_settings import msettings
import json
import os
import signal
import shutil
import datetime


# отмена запущенной сборки
def cancelBuildIso(id=None):
    fLog = open(os.path.join(msettings['BUILD_ISO']['PATH'], str(id) + '.log'), 'r')
    pid = fLog.readlines()[0]
    fLog.close()
    os.kill(int(pid), signal.SIGTERM)
    return True


# получение информации о выполнении сборки
def getActionLog(id=None):
    try:
        fLog = open(os.path.join(msettings['BUILD_ISO']['PATH'], str(id) + '.log'), 'r')
        res = fLog.read()
        # res2 = res.split('\n')
        # if res2[len(res2) - 1] == 'end':
        #     status = 0
        # fLog.close()
        return {'status': 1, 'data': res}
    except:
        return {'status': 0, 'data': ''}


# check params
def checkDir(dir=None):
    if os.path.isdir(dir):
        return True
    else:
        return False

def checkFile(path=None):
    if os.path.isfile(path):
        return True
    else:
        return False

def checkParams(targetDir=None, label=None, relName=None, relShort=None, relVer=None, relLay=False,
                compsFile=None, varFile=None, pkgsetRepos={}):
    if not checkDir(targetDir):
        raise Exception('Target dir does not exist.')
    elif not checkFile(compsFile):
        raise Exception('Comps file does not exist.')
    elif not checkFile(varFile):
        raise Exception('Var file does not exist.')
    elif not label:
        raise Exception('Label is not correct.')
    elif not relName:
        raise Exception('Release name is not correct.')
    elif not relShort:
        raise Exception('Release short is not correct.')
    elif not relVer:
        raise Exception('Release version is not correct.')
    elif not pkgsetRepos:
        raise Exception('Pkgset can not be empty.')
    else:
        for i in pkgsetRepos:
            if len(pkgsetRepos[i]) == 0:
                raise Exception('Pkgset incorrect format.')
        return True

# запуск сборки образа
class executeBuildIso():
    id = None
    target_dir = None
    label = None
    rel_name = None
    rel_short = None
    rel_ver = None
    rel_lay = False
    comps_file = None
    var_file = None
    pkgset_repos = {}
    res = None
    created_at = None

    # очистка данных при отмене
    def clearData(self):
        ind = 0
        baseName = self.rel_short + '-' + self.rel_ver + '-' + self.created_at.strftime("%Y%m%d") + '.'

        if os.path.exists(os.path.join(self.target_dir, baseName + str(ind))):
            while True:
                if os.path.exists(os.path.join(self.target_dir, baseName + str(ind))):
                    ind += 1
                else:
                    ind -= 1
                    shutil.rmtree(os.path.join(self.target_dir, baseName + str(ind)))
                    break


    # генерация файла настроек
    def genConfigFile(self, path=None):

        open(path, 'w').close()

        fConfig = open(path, 'w')
        fConfig.write('# RELEASE\n')
        fConfig.write('release_name = "' + self.rel_name + '"\n')
        fConfig.write('release_short = "' + self.rel_short + '"\n')
        fConfig.write('release_version = "' + self.rel_ver + '"\n')
        fConfig.write('release_is_layered = ' + str(self.rel_lay) + '\n\n')

        fConfig.write('disc_types = {"boot": "netinst", "live": "Live", "dvd": "DVD"}\n\n')

        fConfig.write('# GENERAL SETTINGS\n')
        fConfig.write('comps_file = "' + self.comps_file + '"\n')
        fConfig.write('variants_file = "' + self.var_file + '"\n\n')

        fConfig.write('# KOJI SETTINGS\n')
        fConfig.write('runroot = False\n')
        fConfig.write('koji_profile = "koji"\n\n')

        fConfig.write('# PKGSET\n')
        fConfig.write('sigkeys = [None]\n')
        fConfig.write('pkgset_source = "repos"\n')

        if len(self.pkgset_repos) == 0:
            fConfig.write('pkgset_repos = {}\n\n')
        else:
            fConfig.write('pkgset_repos = ')
            for i in self.pkgset_repos:
                for index, val in enumerate(self.pkgset_repos[i]):
                    self.pkgset_repos[i][index] = 'file://' + val
            fConfig.write(json.dumps(self.pkgset_repos) + '\n\n')

        fConfig.write('# CREATEREPO\n')
        fConfig.write('createrepo_checksum = "sha256"\n\n')

        fConfig.write('# GATHER\n')
        fConfig.write('gather_source = "comps"\n')
        fConfig.write('gather_method = "deps"\n')
        fConfig.write('greedy_method = "build"\n')
        fConfig.write('check_deps = False\n')
        fConfig.write('hashed_directories = True\n')
        fConfig.write('additional_packages = []\n')
        fConfig.write('filter_packages = []\n')
        fConfig.write('multilib = [("^.*$", {"x86_64": ["none"]}), ("^.*$", {"i686": ["none"]})]\n\n')

        fConfig.write('multilib_blacklist = {}\n\n')
        fConfig.write('multilib_whitelist = {}\n\n')

        fConfig.write('# BUILDINSTALL\n')
        fConfig.write('bootable = True\n')
        fConfig.write('buildinstall_method = "lorax"\n\n')

        fConfig.write('# CREATEISO\n')
        fConfig.write('createiso_skip = []\n')
        fConfig.write('create_jigdo = False\n')

        fConfig.close()

    # запуск сборки образа
    def runBuildIso(self):
        # preparation
        compsFileName = os.path.basename(self.comps_file)
        shutil.copyfile(self.comps_file, os.path.join(msettings['BUILD_ISO']['PATH'], compsFileName))
        self.comps_file = os.path.join(msettings['BUILD_ISO']['PATH'], compsFileName)
        # raise Exception('can not be copied ' + compsFile)

        varFileName = os.path.basename(self.var_file)
        shutil.copyfile(self.var_file, os.path.join(msettings['BUILD_ISO']['PATH'], varFileName))
        self.var_file = os.path.join(msettings['BUILD_ISO']['PATH'], varFileName)
        # raise Exception('can not be copied ' + varFile)

        confFile = msettings['BUILD_ISO']['CONFIG_FILE']
        self.genConfigFile(path=confFile)

        self.created_at = datetime.datetime.today()


        cmd = 'sudo -S pungi-koji --target-dir=' + self.target_dir + ' --config ' + confFile + ' --label=' + self.label + ' --supported'
        # cmd = '/home/yarikov/web/testeros/magic/pungidemo.py'


        os.chdir("/tmp/")

        pro = subprocess.Popen('echo sergeyya', stdout=subprocess.PIPE, shell=True)
        proc = subprocess.Popen(cmd, stdin=pro.stdout, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

        logFile = os.path.join(msettings['BUILD_ISO']['PATH'], str(self.id) + '.log')
        open(logFile, 'w').close()

        fLog = open(logFile, 'a')
        fLog.write(str(proc.pid)+'\n')
        fLog.close()

        stdout = []
        while True:
            line = proc.stdout.readline()
            stdout.append(line)
            fLog = open(logFile, 'a')
            fLog.write(line)
            fLog.close()
            if line == '' and proc.poll() != None:
                break

        # os.remove(logFile)
        # os.remove(confFile)
        # os.remove(self.var_file)
        # os.remove(self.comps_file)

        if proc.returncode == 0:
            self.res = 'ok'
        elif proc.returncode == -15:
            self.clearData()
            self.res = 'cancel'
        else:
            raise Exception(stdout[len(stdout) - 2])


    def __init__(self, id=None, targetDir=None, label=None, relName=None, relShort=None, relVer=None, relLay=False,
                 compsFile=None, varFile=None, pkgsetRepos={}):
        try:
            self.id = id
            self.target_dir = targetDir
            self.label = label
            self.rel_name = relName
            self.rel_short = relShort
            self.rel_ver = relVer
            self.comps_file = compsFile
            self.var_file = varFile
            self.pkgset_repos = pkgsetRepos
            self.runBuildIso()

        except Exception as e:
            raise Exception("[BuildIso] {0}".format(e))


# def publicationIso():
#     dir = '/mnt/pub/Temp/RedOS'
#     target_dir = '/mnt/hdd_tmp/tester_build_iso/redos/'
#     ind = 0
#     baseName = 'redos-MUROM-7.1-20180717.0'
#
#     folder = os.path.join(target_dir, baseName)
#     for root, dirs, files in os.walk(folder):
#         for file in files:
#             if file == baseName + '-Everything-x86_64-DVD1.iso':
#                 print os.path.join(root, file)
#
#     # if os.path.exists(os.path.join(target_dir, baseName + str(ind))):
#     #     while True:
#     #         if os.path.exists(os.path.join(target_dir, baseName + str(ind))):
#     #             ind += 1
#     #         else:
#     #             ind -= 1
#     #             os.path.join(target_dir, baseName + str(ind)+'/compose/Everything/x86_64')
#     #
#     #             shutil.copyfile(src, dst)
#     #             break
#
#
# start()

# pkgset = {"x86_64": ["/mnt/hdd/gos_repo/x86_64/os"], "i686": ["/mnt/hdd/gos_repo/x86_64/os"]}
# buildIso = executeBuildIso(id=1, targetDir='/mnt/hdd_tmp/tester_build_iso/fssp/', label='Snapshot-1.0', relName='GosLinux',
#                   relShort='goslinux', relVer='7.1', compsFile='/home/yarikov/build/fssp/comps.xml',
#                   varFile='/home/yarikov/build/fssp/variants.xml.goslinux', pkgsetRepos=pkgset)

# print(cancelBuildIso(id='25'))

#
# print(getActionLog())

import dateutil.parser
# import datetime
#
#
# now = datetime.datetime.now()
# print(now)
# print(now.strftime('%d %B %Y, %H:%M'))

# print("{}.{}.{}  {}:{}".format(now.day, now.month, now.year, now.hour, now.minute))
