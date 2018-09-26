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
    command = command.split()
    # cmd1 = Popen(['echo', rootPass], stdout=PIPE)
    cmd2 = Popen(['sudo', '-S'] + command, stdout=PIPE)

    output, error = cmd2.communicate()
    if error:
        raise Exception(error)


def runBashFromUser(user_name=None, command=None):
    #command = command.split()
    #cmd1 = Popen(['echo', user1Pass], stdout=PIPE)
    cmd = Popen("su -l " + user_name + " -c '" + command + "'", stdin=PIPE, stdout=PIPE, shell=True)

    output, error = cmd.communicate()

    return cmd.returncode


# INPUT DATA
while True:
    user1Name = raw_input("Имя первого пользователя: ")
    if checkUser(user1Name) == 1:
        print('Пользователь с таким именем не найден')
    else:
        break

while True:
    user2Name = raw_input("Имя второго пользователя: ")
    if checkUser(user2Name) == 1:
        print('Пользователь с таким именем не найден')
    else:
        break


# RUNNING
result = []


def getCodeRunCommand(u_name=None, command=None):
    code = runBashFromUser(user_name=u_name, command=command)
    # print code
    if code == 1:
        return 0
    elif code == 2:
        return 0
    elif code == 126:
        return 0
    else:
        return 1
    # 0 - close access
    # 1 - open access


def runAnalis(p1=0, p2=0, u_name=None):
    print('[user: ' + u_name + '; action: read; file: read_only.txt]')
    if getCodeRunCommand(u_name=u_name, command='cat /tmp/acl_root.txt') != p1:
        result.append('user: ' + u_name + '; action: read; file: acl_root.txt')

    print('[user: ' + u_name + '; action: write; file: read_only.txt]')
    if getCodeRunCommand(u_name=u_name, command='echo "123" >> /tmp/acl_root.txt') != p2:
        result.append('user: ' + u_name + '; action: write; file: acl_root.txt')


print('Тестирование ФБО «Защита данных пользователя»')
print('Дискреционное управление доступом - ACL\n\n')

print('Пункт а')
runBashFromRoot(command='touch /tmp/acl_root.txt')
runBashFromRoot(command='chmod 660 /tmp/acl_root.txt')

runAnalis(u_name=user1Name)
runAnalis(u_name=user2Name)
print('\n')

print('Пункт б')
runBashFromRoot(command='setfacl -m u:' + user1Name + ':r-- /tmp/acl_root.txt')
runBashFromRoot(command='setfacl -m g:' + user2Name + ':-w- /tmp/acl_root.txt')

runAnalis(u_name=user1Name, p1=1)
runAnalis(u_name=user2Name, p2=1)


# CLEAR
file1 = "/tmp/acl_root.txt"
if os.path.isfile(file1):
    os.remove(file1)


# OUTPUT DATA
print('\n')
print('РЕЗУЛЬТАТ ТЕСТИРОВАНИЯ')
if len(result) != 0:
    print('при прохождении теста произошли ошибки:')
    for i in result:
        print i
else:
    print('тест пройден успешно')

