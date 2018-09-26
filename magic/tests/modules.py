#!/usr/bin/python
# coding: utf_8


from subprocess import Popen, PIPE
import sys, getopt, datetime
import os, shutil, pwd
from threading import Thread
import json
import time



# РАБОТА С ТЕСТАМИ (запуск, выполнение команд, вывод ошибок, вывод результата)
class runTest(object):

    OSF = None
    testName = None
    testNum = None
    testVer = None

    sshClient = None
    sshHostName = None
    sshUserName = None

    installPkg = False
    mountPoint = False

    params = {}

    result = []


    # ЗАПУСК КОМАНД-----------------------------------------------------------------------------------------------------
    # запуск и анализ команд
    def runCmd(self, ssh=False, user='root', cmd=None, out=None, code=None, remov=False):

        if not ssh:
            if user == 'root':
                cmd1 = "sudo -S " + cmd
            else:
                cmd1 = "su -l " + user + " -c '" + cmd + "'"

            proc = Popen(cmd1, stdout=PIPE, stderr=PIPE, shell=True)
            output, error = proc.communicate()
            output = output.rstrip()
            error = error.rstrip()
            returnCode = proc.returncode
            pid = proc.pid

        else:
            stdin, stdout, stderr = self.sshClient.exec_command(cmd)
            output = stdout.read().rstrip()
            error = stderr.read().rstrip()
            returnCode = stdout.channel.recv_exit_status()
            pid = None
            user = '%s' % self.sshUserName
            cmd = '%s: %s' % (self.sshHostName, cmd)



        if out != '':
            if out == None:
                if error:
                    res = error.rstrip()
                else:
                    res = output.rstrip()
            else:
                if code == returnCode:
                    res = out
                else:
                    res = 'no'
            # print('user:[%s]\tcmd:[%s] res:[%s]' % (user, cmd, res))
            print("{0:<10}{1:<81}{2:<3}".format(user, cmd, ' ' + res))


        if code != None and code != returnCode:
            self.result.append(dict(type='code', user=user, cmd=cmd, output=output, error=error,
                                    wait=code, taken=returnCode, remov=remov))
            if ssh:
                self.sshClient.close()

            addRecordToErrorLog(dict(test=self.testNum, user=user, cmd=cmd, output=output, error=error,
                                     wait=code, taken=returnCode))

            if not remov:
                raise Exception('')




        return {'output': output, 'error': error, 'code': returnCode, 'pid': pid}

    # запуск команд от root
    def runCmdFromRoot(self, cmd=None, out=None, code=None, remov=False):
        return self.runCmd(cmd=cmd, out=out, code=code, remov=remov)

    # запуск команд от пользователя
    def runCmdFromUser(self, user=None, cmd=None, out=None, code=None):
        return self.runCmd(user=user, cmd=cmd, out=out, code=code)

    # запуск команд от первого пользователя
    def runCmdFirstUser(self, cmd=None, out=None, code=None):
        return self.runCmd(user=self.params['firstUser'], cmd=cmd, out=out, code=code)

    # запуск команд от второго пользователя
    def runCmdSecondUser(self, cmd=None, out=None, code=None):
        return self.runCmd(user=self.params['secondUser'], cmd=cmd, out=out, code=code)


    # РАБОТА ПО SSH-----------------------------------------------------------------------------------------------------
    # создание ssh соединения
    def sshConnect(self, host=None, user=None, passwd=None, port=None):
        import paramiko
        self.sshClient = paramiko.SSHClient()
        self.sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sshHostName = host
        self.sshUserName = user
        self.sshClient.connect(hostname=host, username=user, password=passwd, port=port)

    # выполнение команд по ssh
    def sshRunCmd(self, cmd=None, out=None, code=None):
        return self.runCmd(ssh=True, cmd=cmd, out=out, code=code)

    # закрытие ssh соединения
    def sshDisconnect(self):
        self.sshClient.close()


    # РАБОТА С ПАКЕТОМ--------------------------------------------------------------------------------------------------
    # установка пакета
    def installPack(self, packName=None):
        if self.runCmdFromRoot(cmd="rpm -qi %s" % packName, out='')['code'] == 1:
            self.runCmdFromRoot(cmd="yum install %s -y" % packName, out='ok', code=0)
            self.installPkg = True

    # удаление пакета
    def uninstallPack(self, packName=None):
        if self.installPkg:
            self.runCmdFromRoot(cmd="yum remove %s -y" % packName, out='ok', code=0, remov=True)
        self.installPack = False


    # РАБОТА С НОСИТЕЛЕМ------------------------------------------------------------------------------------------------
    # монтирование носителя
    def mountDev(self, name=None, point=None, key=''):
        self.mountPoint = self.runCmdFromRoot(cmd="lsblk %s -n --output MOUNTPOINT" % name, out='ok', code=0)['output'].rstrip()
        if self.mountPoint != '':
            self.runCmdFromRoot(cmd="umount %s" % name, out='ok', code=0)
            time.sleep(3)
            self.runCmdFromRoot(cmd='rm -rf %s' % self.mountPoint, out='ok', code=0)

        if key == '':
            key = '-t ext4 -o defaults'

        self.runCmdFromRoot(cmd="mount %s %s %s" % (key, name, point), out='ok', code=0)
        time.sleep(3)

    # отмонтирование носителя
    def umountDev(self, name=None, remov=False):
        mp = self.runCmdFromRoot(cmd="lsblk %s -n --output MOUNTPOINT" % name, out='ok', code=0)['output'].rstrip()
        if mp != '':
            self.runCmdFromRoot(cmd="umount %s" % name, out='ok', code=0, remov=remov)
            time.sleep(3)

        if self.mountPoint != '':
            self.runCmdFromRoot(cmd="mkdir %s" % self.mountPoint, out='ok', code=0, remov=remov)
            self.runCmdFromRoot(cmd="mount -t ext4 -o defaults %s %s" % (name, self.mountPoint), out='ok', code=0, remov=remov)
            time.sleep(3)
            self.mountPoint = ''


    # ВЫВОД ИНФОРМАЦИИ--------------------------------------------------------------------------------------------------
    # показать стартовый блок
    def showInfoBlock(self):
        print('*' * 37 + ' ИНФОРМАЦИЯ О ТЕСТЕ ' + '*' * 37)
        print('ФБО:\t%s' % self.testOSF)
        print('Имя:\t%s' % self.testName)
        print('Версия:\t%s' % self.testVer)
        print('Номер:\t%s' % self.testNum)

    # показать блок с настройками
    def showSetUpBlock(self):
        print('*' * 41 + ' НАСТРОЙКА ' + '*' * 42)

        if 'testDir' in self.params:
            self.createTestDir()


    # показать блок тестирвоания
    def showTestingBlock(self):
        print('*' * 40 + ' ТЕСТИРОВАНИЕ ' + '*' * 40)

    # показать блок отката изменений
    def showEndBlock(self):
        print('*' * 31 + ' ОТКАТ ПРОИЗВЕДЕННЫХ ИЗМЕНЕНИЙ ' + '*' * 32)


    # показть блок с результатом
    def showResultBlock(self):
        if 'testDir' in self.params:
            self.deleteTestDir()

        print('*' * 35 + ' РЕЗУЛЬТАТ ТЕСТИРОВАНИЯ ' + '*' * 35)

        status = 0

        if len(self.result) != 0:
            print('Статус: НЕ ПРОЙДЕН\n')
            for i in self.result:
                if i['type'] == 'code':
                    print('user:\t%s' % i['user'])
                    print('cmd:\t%s' % i['cmd'])
                    print('wait:\t%s' % i['wait'])
                    print('taken:\t%s' % i['taken'])
                    if i['output'] != '':
                        print('output:\t%s' % i['output'])
                    if i['error'] != '':
                        print('error:\t%s' % i['error'])
                    if not i['remov']:
                        status = 1
                elif i['type'] == 'general':
                    print('msg:\t%s' % i['msg'])
                    if i['wait'] != '':
                        print('wait:\t%s' % i['wait'])
                    if i['taken'] != '':
                        print('taken:\t%s' % i['taken'])
                    status = 1
                elif i['type'] == 'error':
                    print('error:\t%s' % i['msg'])
                    status = 2

                print('\n')
        else:
            print('Статус: ПРОЙДЕН\n')

        sys.exit(status)

    # блок с информацией о невозможжности выполнения теста
    def showCanNotMessage(self):
        print('*' * 35 + ' РЕЗУЛЬТАТ ТЕСТИРОВАНИЯ ' + '*' * 35)
        print('Невозможно выполнить тест в автоматическом режиме')
        sys.exit(4)



    # РАБОТА С КАТАЛОГОМ------------------------------------------------------------------------------------------------
    def createTestDir(self):
        if os.path.exists("%s" % self.params['testDir']):
            shutil.rmtree("%s" % self.params['testDir'])

        self.runCmdFromRoot(cmd="mkdir %s" % self.params['testDir'], out='ok', code=0)

    def deleteTestDir(self):
        self.runCmdFromRoot(cmd='rm -rf %s' % self.params['testDir'], out='ok', code=0, remov=True)






    # --------------------------------------------------------------------------------------------------
    def addResult(self, msg=None, wait='', taken=''):
        self.result.append(dict(type='general', msg=msg, wait=wait, taken=taken))
        raise Exception('')

    def showActionMsg(self, msg=None):
        # print('user:root action:%s res:ok' % msg)
        print("{0:<10}{1:<81}{2:<3}".format('root', 'action: ' + msg, ' ok'))

    def showError(self, error=None):
        print('Тестирование прервано, произошла ошибка')
        if error.message != '':
            self.result.append(dict(type='error', msg=error.message))

    def setPause(self, params={}):
        setContinueLogFile(params=params)
        print('Для продолжения тестирования необходимо произвести перезагрузку ОС.')
        sys.exit(3)

    def getAddParams(self):
        return getAddParams()




    def __init__(self, osf=None, name=None, num=None, ver=None, params=None):
        self.params = checkParams(params=params, testNum=num)
        self.testOSF = osf
        self.testName = name
        self.testNum = num
        self.testVer = ver







# работа с потоками
class MyThread(Thread):

    pid = None

    def run(self):
        print("{0:<10}{1:<81}{2:<3}".format(self.user, self.cmd, ' ok'))

        proc = Popen("%s" % self.cmd, stdout=PIPE, shell=True)
        self.pid = proc.pid
        output, error = proc.communicate()


    def __init__(self, user=None, cmd=None):
        Thread.__init__(self)
        self.user = user
        self.cmd = cmd