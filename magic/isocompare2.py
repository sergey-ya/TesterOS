#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, re, isoparser, shutil
import createrepo_c as cr
from datetime import datetime


# создает класс доступа к данным на iso образе
class accessIso():
    dir = "/home/yarikov/mnt2"

    isoPath = None
    mountDir = None
    isoName = None

    def getIsoSystem(self):
        return self.isoName


    def getPkgLst(self):
        md = cr.Metadata()
        md.locate_and_load_xml(self.mountDir)
        res = []
        for key in md.keys():
            pkg = md.get(key)
            res.append(dict(nvra=pkg.nvra(), name=pkg.name, ver=pkg.version, rel=pkg.release, checksum=pkg.pkgId,
                            checksumType=pkg.checksum_type, arch=pkg.arch, epoch=pkg.epoch))
        return res


    def generateMounthDir(self, path):
        i = 0
        while True:
            i += 1
            res = path + "/iso" + str(i) + '/'
            if not os.path.exists(res):
                break
        return res


    def getRepodata(self):

        def saveFile(file_name=None, content=None):
            file = open(self.mountDir + 'repodata/' + file_name, 'w')
            file.write(content)
            file.close()

        if not os.path.exists(self.mountDir):
            os.mkdir(self.mountDir)
        if not os.path.exists(self.mountDir + 'repodata/'):
            os.mkdir(self.mountDir + 'repodata/')

        iso = isoparser.parse(self.isoPath)
        for child in iso.record("repodata").children:
            saveFile(file_name=child.name, content=iso.record("repodata", child.name).content)
        iso.close()

        # # raise Exception("Нет такого файла iso")
        #
        # # проверка существования
        # if not os.path.exists(self.isoPath):
        #     raise Exception(u"Файл образа не найден: " + self.isoPath)
        #
        # # создание каталога для монтирования
        # if not os.path.exists(self.mountDir):
        #     os.mkdir(self.mountDir)
        #
        # proc = Popen("echo sergeyya | sudo losetup /dev/loop10 " + self.isoPath, shell=True, stdout=PIPE, stderr=PIPE)
        # proc = Popen("echo sergeyya | sudo -S mount " + self.isoPath + " " + self.mountDir,
        # # proc = Popen("echo sergeyya | sudo -S mount -o loop -t iso9660 " + self.isoPath + " " + self.mountDir,
        #              shell=True, stdout=PIPE, stderr=PIPE)
        #
        # output, error = proc.communicate()
        # if error:
        #     raise Exception(u"Неудачная попытка монтирования: " + self.isoPath)


    # def check(self):
    #     # проверка образа
    #     try:
    #         file = open(self.mountDir + '/media.repo')
    #     except IOError as e:
    #         self.umount()
    #         raise Exception("Неверный формат образа: " + self.isoPath)
    #
    #     line = file.readlines()
    #     file.close()
    #     iso_name = line[1]
    #     self.isoName = iso_name[5:len(iso_name) - 1:1]
    #
    #     try:
    #         md = cr.Metadata()
    #         md.locate_and_load_xml(self.mountDir)
    #     except IOError as e:
    #         self.umount()
    #         raise Exception("Ошибка чтения образа: " + self.isoPath)


    def delRepodata(self):
        shutil.rmtree(self.mountDir)


    def __init__(self, iso_path):
        try:
            self.isoPath = iso_path
            self.mountDir = self.generateMounthDir(self.dir)
            self.getRepodata()
            # self.check()
        except Exception as e:
            raise Exception(e)

    def __del__(self):
        self.delRepodata()



# ПОИСК ДОСТУПНЫХ ОБРАЗОВ
def getIsoLst(dir=None):
    try:
        dir = os.path.normpath(dir)

        month_list = [u'января', u'февраля', u'марта', u'апреля', u'мая', u'июня',
                      u'июля', u'августа', u'сентября', u'октября', u'ноября', u'декабря']

        res = []
        for elem in os.listdir(dir):
            if re.findall(r'\d{2}.\d{2}.\d{4}', elem):
                for file in os.listdir(dir + '/' + elem + '/'):
                    if file.endswith(".iso"):
                        dat = elem.split('.')
                        res.append(dict(date=elem, path=os.path.join(dir + '/' + elem + '/', file),
                                        dateFormat=dat[0] + ' ' + month_list[int(dat[1]) - 1] + ' ' + dat[2],
                                        name=file))

        res.sort(key=lambda date: datetime.strptime(date['date'], "%d.%m.%Y"), reverse=True)
        return res

    except Exception as e:
        return None

# example
# print(getIsoLst(dir='/mnt/pub/Temp/GosLinux'))



# ПОИСК ПАКЕТОВ НА ОБРАЗЕ
def searchPkgOnIso(iso_path=None, pkg_mask=None):
    iso = accessIso(iso_path)

    # разбиывает маску и удаляет повторяющиеся элементы
    pkg_mask = pkg_mask.split()
    r = []
    for pkg in pkg_mask:
        filt = filter(lambda x: pkg in x, pkg_mask)
        newList = sorted(filt, key=len)
        r.append(newList[-1])
    pkg_mask = [e for i, e in enumerate(r) if e not in r[:i]]

    res = []
    for index, p in enumerate(pkg_mask):
        res.append(dict(id=index, mask=str(p), status='0', pkgs=[]))

    pkgLstOnIso = iso.getPkgLst()
    for pkg in pkgLstOnIso:
        for elem in res:
            if elem['mask'] in pkg['nvra']:
                elem['status'] = '1'
                elem['pkgs'].append(pkg['nvra'])

    del iso
    return res

# example
# print(searchPkgOnIso(iso_path='/mnt/pub/Temp/GosLinux/17.04.2018/goslinux-7.1-20180417.0-Everything-x86_64-DVD1.iso',
#                      pkg_mask='123 samba 1'))



# СРАВНЕНИЕ ДВУХ ОБРАЗОВ
def compareIso(iso1_path=None, iso2_path=None):

    def comparePkgLst(pkg_lst1, pkg_lst2):
        iso1_pkgs = []
        iso2_pkgs = []
        ver = []
        rel = []
        checksum = []

        for pkg1 in pkg_lst1:
            for pkg2 in pkg_lst2:
                if (pkg1['name'] == pkg2['name']) and (pkg1['arch'] == pkg2['arch']):
                    if (pkg1['ver'] != pkg2['ver']) or (pkg1['epoch'] != pkg2['epoch']):
                        ver.append(dict(name=pkg1['name'] + '(' + pkg1['arch'] + ')',
                                        iso1=pkg1['epoch'] + ':' + pkg1['ver'],
                                        iso2=pkg1['epoch'] + ':' + pkg2['ver']))
                        pkg_lst2.remove(pkg2)
                        mark = 0
                        break
                    elif pkg1['rel'] != pkg2['rel']:
                        rel.append(dict(name=pkg1['name'] + '(' + pkg1['arch'] + ')',
                                        iso1=pkg1['rel'], iso2=pkg2['rel']))
                        pkg_lst2.remove(pkg2)
                        mark = 0
                        break
                    elif pkg1['checksum'] != pkg2['checksum']:
                        checksum.append(dict(name=pkg1['name'] + '(' + pkg1['arch'] + ')',
                                             iso1=pkg1['checksum'], iso2=pkg2['checksum'],
                                             checksum_type=pkg1['checksumType'],
                                             iso1_short=pkg1['checksum'][0:20] + '...',
                                             iso2_short=pkg2['checksum'][0:20] + '...'))
                        pkg_lst2.remove(pkg2)
                        mark = 0
                        break
                    else:
                        pkg_lst2.remove(pkg2)
                        mark = 0
                        break
                else:
                    mark = 1

            if mark == 1:
                iso1_pkgs.append(pkg1['nvra'])

        for pkg in pkg_lst2:
            iso2_pkgs.append(pkg['nvra'])

        iso1_pkgs.sort()
        iso2_pkgs.sort()

        ver.sort(key=lambda key: key['name'])
        rel.sort(key=lambda key: key['name'])
        checksum.sort(key=lambda key: key['name'])

        res = dict(iso1_pkgs=iso1_pkgs, iso2_pkgs=iso2_pkgs, ver=ver, rel=rel, checksum=checksum)
        return res

    try:
        if iso1_path == iso2_path:
            raise Exception(u"Вы пытаетесь сравнить образ сам с собой")

        iso1 = accessIso(iso1_path)
        iso2 = accessIso(iso2_path)

        if iso1.getIsoSystem() != iso2.getIsoSystem():
            raise Exception(u"Вы пытаетесь сравнить различные системы")

        return comparePkgLst(iso1.getPkgLst(), iso2.getPkgLst())

    except Exception as e:
        raise Exception(e)

    finally:
        del iso1
        del iso2

# example
# print (compareIso(iso1_path='/mnt/pub/Temp/GosLinux/17.04.2018/goslinux-7.1-20180417.0-Everything-x86_64-DVD1.iso',
#                   iso2_path='/mnt/pub/Temp/GosLinux/22.03.2018/goslinux-7.1-20180322.0-Everything-x86_64-DVD1.iso'))