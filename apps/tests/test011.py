#!/usr/bin/python
# coding: utf_8

import os, shutil, pwd
from subprocess import Popen, PIPE

version = '0.1'
test_dir = "/tmp/test_test"


def checkUser(u_name=None):
    for p in pwd.getpwall():
        if u_name == p[0]:
            return 0
    return 1


def runBashFromRoot(command=None):
    try:
        # command = command.split()
        # cmd1 = Popen(['echo', rootPass], stdout=PIPE)
        # cmd2 = Popen(['sudo', '-S'] + command, stdout=PIPE)
        cmd = Popen("sudo -S " + command, stdout=PIPE, shell=True)

        output, error = cmd.communicate()
        return cmd.returncode

        if error:
            raise Exception(error)
    except:
        return 100


def runBashFromUser(user_name=None, command=None):
    #command = command.split()
    #cmd1 = Popen(['echo', user1Pass], stdout=PIPE)
    cmd = Popen("su -l " + user_name + " -c '" + command + "'", stdin=PIPE, stdout=PIPE, shell=True)

    output, error = cmd.communicate()

    return cmd.returncode


# INPUT DATA
user1Name = 'user'
user2Name = 'user2'
mntDevice = '/dev/sdb1'
# while True:
#     user1Name = raw_input("Имя первого пользователя: ")
#     if checkUser(user1Name) == 1:
#         print('Пользователь с таким именем не найден')
#     else:
#         break
#
# while True:
#     user2Name = raw_input("Имя второго пользователя: ")
#     if checkUser(user2Name) == 1:
#         print('Пользователь с таким именем не найден')
#     else:
#         break

# SETTINGS
runBashFromRoot("mkdir %s" % test_dir)


# RUNNING
result = []

print('Тестирование ФБО «Защита данных пользователя»')
print('Дискреционное управление доступом — дополнительные правила\n\n')

print('Пункт а')
runBashFromRoot("mkdir %s/mnt" % test_dir)
runBashFromRoot("mkdir %s/mnt/disk_ext" % test_dir)
runBashFromRoot("chmod 777 %s/mnt/disk_ext" % test_dir)
runBashFromRoot("mount -r %s %s/mnt/disk_ext" % (mntDevice, test_dir))

if runBashFromRoot("touch %s/mnt/disk_ext/test.txt" % test_dir) != 1:
    result.append('item: а; action: create; object: test.txt')

if runBashFromRoot("mkdir %s/mnt/disk_ext/dir" % test_dir) != 1:
    result.append('item: а; action: create; object: dir')

runBashFromRoot("umount %s" % mntDevice)
print('\n')

print('Пункт б')
runBashFromRoot("touch %s/imm.txt" % test_dir)
runBashFromRoot("chattr +i %s/imm.txt" % test_dir)

if runBashFromRoot("echo 123 >> %s/imm.txt" % test_dir) != 1:
    result.append('item: б; action: write; object: imm.txt')

if runBashFromRoot("rm %s/imm.txt" % test_dir) != 1:
    result.append('item: б; action: delete; object: imm.txt')


runBashFromRoot("chattr -i %s/imm.txt" % test_dir)
runBashFromRoot("rm %s/imm.txt" % test_dir)


# CLEAR
shutil.rmtree("%s" % test_dir)


# OUTPUT DATA
print('\n')
print('РЕЗУЛЬТАТ ТЕСТИРОВАНИЯ')
if len(result) != 0:
    print('при прохождении теста произошли ошибки:')
    for i in result:
        print i
else:
    print('тест пройден успешно')

