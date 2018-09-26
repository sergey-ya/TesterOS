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


#SETTINGS
if os.path.exists("%s" % test_dir):
    shutil.rmtree("%s" % test_dir)

runBashFromRoot("mkdir %s" % test_dir)
runBashFromRoot("mkdir %s/dir_wr" % test_dir)
runBashFromRoot("chmod 330 %s/dir_wr/" % test_dir)
runBashFromRoot("mkdir %s/dir_read" % test_dir)
runBashFromRoot("chmod 440 %s/dir_read/" % test_dir)
runBashFromRoot("mkdir %s/dir_wr_read" % test_dir)
runBashFromRoot("chmod 660 %s/dir_wr_read/" % test_dir)
runBashFromRoot("mkdir %s/dir_exec" % test_dir)
runBashFromRoot("chmod 110 %s/dir_exec/" % test_dir)

runBashFromRoot("mkdir %s/tst_fldr/" % test_dir)
runBashFromRoot("touch %s/tst_fldr/read_only.txt" % test_dir)
runBashFromRoot("chmod 440 %s/tst_fldr/read_only.txt" % test_dir)
# runBashFromRoot("chmod 777 %s/tst_fldr/read_only.txt" % test_dir)
runBashFromRoot("touch %s/tst_fldr/rw.txt" % test_dir)
runBashFromRoot("chmod 660 %s/tst_fldr/rw.txt" % test_dir)
runBashFromRoot("touch %s/tst_fldr/write_only.txt" % test_dir)
runBashFromRoot("chmod 220 %s/tst_fldr/write_only.txt" % test_dir)
runBashFromRoot("touch %s/tst_fldr/exec_only.sh" % test_dir)
runBashFromRoot("chmod 550 %s/tst_fldr/exec_only.sh" % test_dir)


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

def runAnalis(p1=0, p2=0, p3=0, p4=0, p5=0, p6=0, p7=0, p8=0, p9=0, p10=0, p11=0, p12=0, u_name=None, item=None):
    # read
    print('[user: ' + u_name + '; action: read; file: read_only.txt]')
    if getCodeRunCommand(u_name=u_name, command="cat %s/tst_fldr/read_only.txt" % test_dir) != p1:
        result.append('item: ' + item + '; user: ' + u_name + '; action: read; file: read_only.txt')

    print('[user: ' + u_name + '; action: read; file: rw.txt]')
    if getCodeRunCommand(u_name=u_name, command="cat %s/tst_fldr/rw.txt" % test_dir) != p2:
        result.append('item: ' + item + '; user: ' + u_name + '; action: read; file: rw.txt')

    print('[user: ' + u_name + '; action: read; file: write_only.txt]')
    if getCodeRunCommand(u_name=u_name, command="cat %s/tst_fldr/write_only.txt" % test_dir) != p3:
        result.append('item: ' + item + '; user: ' + u_name + '; action: read; file: write_only.txt')

    print('[user: ' + u_name + '; action: read; file: exec_only.sh]')
    if getCodeRunCommand(u_name=u_name, command="cat %s/tst_fldr/exec_only.sh" % test_dir) != p4:
        result.append('item: ' + item + '; user: ' + u_name + '; action: read; file: exec_only.sh')

    # write
    print('[user: ' + u_name + '; action: write; file: read_only.txt]')
    if getCodeRunCommand(u_name=u_name, command="echo 'txt' > %s/tst_fldr/read_only.txt" % test_dir) != p5:
        result.append('item: ' + item + '; user: ' + u_name + '; action: write; file: read_only.txt')

    print('[user: ' + u_name + '; action: write; file: rw.txt]')
    if getCodeRunCommand(u_name=u_name, command="echo 'txt' > %s/tst_fldr/rw.txt" % test_dir) != p6:
        result.append('item: ' + item + '; user: ' + u_name + '; action: write; file: rw.txt')

    print('[user: ' + u_name + '; action: write; file: write_only.txt]')
    if getCodeRunCommand(u_name=u_name, command="echo 'txt' > %s/tst_fldr/write_only.txt" % test_dir) != p7:
        result.append('item: ' + item + '; user: ' + u_name + '; action: write; file: write_only.txt')

    print('[user: ' + u_name + '; action: write; file: exec_only.sh]')
    if getCodeRunCommand(u_name=u_name, command="echo 'txt' > %s/tst_fldr/exec_only.sh" % test_dir) != p8:
        result.append('item: ' + item + '; user: ' + u_name + '; action: write; file: exec_only.sh')

    # execute
    print('[user: ' + u_name + '; action: execute; file: read_only.txt]')
    if getCodeRunCommand(u_name=u_name, command="%s/tst_fldr/read_only.txt" % test_dir) != p9:
        result.append('item: ' + item + '; user: ' + u_name + '; action: execute; file: read_only.txt')

    print('[user: ' + u_name + '; action: execute; file: rw.txt]')
    if getCodeRunCommand(u_name=u_name, command="%s/tst_fldr/rw.txt" % test_dir) != p10:
        result.append('item: ' + item + '; user: ' + u_name + '; action: execute; file: rw.txt')

    print('[user: ' + u_name + '; action: execute; file: write_only.txt]')
    if getCodeRunCommand(u_name=u_name, command="%s/tst_fldr/write_only.txt" % test_dir) != p11:
        result.append('item: ' + item + '; user: ' + u_name + '; action: execute; file: write_only.txt')

    print('[user: ' + u_name + '; action: execute; file: exec_only.sh]')
    if getCodeRunCommand(u_name=u_name, command="%s/tst_fldr/exec_only.sh" % test_dir) != p12:
        result.append('item: ' + item + '; user: ' + u_name + '; action: execute; file: exec_only.sh')

def runAnalis2(p1=0, p2=0, p3=0, p4=0, p5=0, p6=0, p7=0, p8=0, p9=0, p10=0, p11=0, p12=0, u_name=None, item=None):
    # read
    print('[user: ' + u_name + '; action: read; dir: dir_read]')
    if getCodeRunCommand(u_name=u_name, command="ls -l %s/dir_read/" % test_dir) != p1:
        result.append('item: ' + item + '; user: ' + u_name + '; action: read; dir: dir_read')

    print('[user: ' + u_name + '; action: read; dir: dir_wr_read]')
    if getCodeRunCommand(u_name=u_name, command="ls -l %s/dir_wr_read/" % test_dir) != p2:
        result.append('item: ' + item + '; user: ' + u_name + '; action: read; dir: dir_wr_read')

    print('[user: ' + u_name + '; action: read; dir: dir_wr]')
    if getCodeRunCommand(u_name=u_name, command="ls -l %s/dir_wr/" % test_dir) != p3:
        result.append('item: ' + item + '; user: ' + u_name + '; action: read; dir: dir_wr')

    print('[user: ' + u_name + '; action: read; dir: dir_exec]')
    if getCodeRunCommand(u_name=u_name, command="ls -l %s/dir_exec/" % test_dir) != p4:
        result.append('item: ' + item + '; user: ' + u_name + '; action: read; dir: dir_exec')

    # write
    print('[user: ' + u_name + '; action: write; dir: dir_read]')
    if getCodeRunCommand(u_name=u_name, command="touch %s/dir_read/test.txt" % test_dir) != p5:
        result.append('item: ' + item + '; user: ' + u_name + '; action: write; dir: dir_read')

    print('[user: ' + u_name + '; action: write; dir: dir_wr_read]')
    if getCodeRunCommand(u_name=u_name, command="touch %s/dir_wr_read/test.txt" % test_dir) != p6:
        result.append('item: ' + item + '; user: ' + u_name + '; action: write; dir: dir_wr_read')

    print('[user: ' + u_name + '; action: write; dir: dir_wr]')
    if getCodeRunCommand(u_name=u_name, command="touch %s/dir_wr/test.txt" % test_dir) != p7:
        result.append('item: ' + item + '; user: ' + u_name + '; action: write; dir: dir_wr')

    print('[user: ' + u_name + '; action: write; dir: dir_exec]')
    if getCodeRunCommand(u_name=u_name, command="touch %s/dir_exec/test.txt" % test_dir) != p8:
        result.append('item: ' + item + '; user: ' + u_name + '; action: write; dir: dir_exec')

    # cd
    print('[user: ' + u_name + '; action: cd; dir: dir_read]')
    if getCodeRunCommand(u_name=u_name, command="cd %s/dir_read/" % test_dir) != p9:
        result.append('item: ' + item + '; user: ' + u_name + '; action: cd; dir: dir_read')

    print('[user: ' + u_name + '; action: cd; dir: dir_wr_read]')
    if getCodeRunCommand(u_name=u_name, command="cd %s/dir_wr_read/" % test_dir) != p10:
        result.append('item: ' + item + '; user: ' + u_name + '; action: cd; dir: dir_wr_read')

    print('[user: ' + u_name + '; action: cd; dir: dir_wr]')
    if getCodeRunCommand(u_name=u_name, command="cd %s/dir_wr/" % test_dir) != p11:
        result.append('item: ' + item + '; user: ' + u_name + '; action: cd; dir: dir_wr')

    print('[user: ' + u_name + '; action: cd; dir: dir_exec]')
    if getCodeRunCommand(u_name=u_name, command="cd %s/dir_exec/" % test_dir) != p12:
        result.append('item: ' + item + '; user: ' + u_name + '; action: cd; dir: dir_exec')

    # удаляем данные из каталогов
    file1 = "%s/dir_read/test.txt" % test_dir
    file2 = "%s/dir_wr_read/test.txt" % test_dir
    file3 = "%s/dir_wr/test.txt" % test_dir
    file4 = "%s/dir_exec/test.txt" % test_dir
    if os.path.isfile(file1):
        os.remove(file1)
    if os.path.isfile(file2):
        os.remove(file2)
    if os.path.isfile(file3):
        os.remove(file3)
    if os.path.isfile(file4):
        os.remove(file4)



print('Тестирование ФБО «Защита данных пользователя»')
print('Дискреционное управление доступом — общий механизм')

print('Пункт а')
runAnalis(u_name=user1Name, item='а')
runAnalis(u_name=user2Name, item='а')
print('\n')

print('Пункт б')
runBashFromRoot("chown -R " + user1Name + " %s/tst_fldr/" % test_dir)
runAnalis(u_name=user1Name, item='б', p1=1, p2=1, p4=1, p6=1, p7=1, p12=1)
runAnalis(u_name=user2Name, item='б')
print('\n')

print('Пункт в')
runBashFromRoot("chown -R root:" + user1Name + " %s/tst_fldr/" % test_dir)
runAnalis(u_name=user1Name, item='в', p1=1, p2=1, p4=1, p6=1, p7=1, p12=1)
runAnalis(u_name=user2Name, item='в')
print('\n')

print('Пункт г')
runBashFromRoot("usermod -a -G audio " + user1Name)
runBashFromRoot("usermod -a -G audio " + user2Name)
runBashFromRoot("chown -R root:audio %s/tst_fldr/" % test_dir)
runAnalis(u_name=user1Name, item='г', p1=1, p2=1, p4=1, p6=1, p7=1, p12=1)
runAnalis(u_name=user2Name, item='г', p1=1, p2=1, p4=1, p6=1, p7=1, p12=1)
print('\n')

print('Пункт д')
runAnalis2(u_name=user1Name, item='д')
runAnalis2(u_name=user2Name, item='д')
print('\n')

print('Пункт е')
runBashFromRoot("chown " + user1Name + " %s/dir_read/" % test_dir)
runBashFromRoot("chown " + user1Name + " %s/dir_wr_read/" % test_dir)
runBashFromRoot("chown " + user1Name + " %s/dir_wr/" % test_dir)
runBashFromRoot("chown " + user1Name + " %s/dir_exec/" % test_dir)
runAnalis2(u_name=user1Name, item='е', p1=1, p2=1, p7=1, p11=1, p12=1)
runAnalis2(u_name=user2Name, item='е')
print('\n')

print('Пункт ж')
runBashFromRoot("chown root:" + user1Name + " %s/dir_read/" % test_dir)
runBashFromRoot("chown root:" + user1Name + " %s/dir_wr_read/" % test_dir)
runBashFromRoot("chown root:" + user1Name + " %s/dir_wr/" % test_dir)
runBashFromRoot("chown root:" + user1Name + " %s/dir_exec/" % test_dir)
runAnalis2(u_name=user1Name, item='ж', p1=1, p2=1, p7=1, p11=1, p12=1)
runAnalis2(u_name=user2Name, item='ж')
print('\n')

print('Пункт з')
runBashFromRoot("chown root:audio %s/dir_read/" % test_dir)
runBashFromRoot("chown root:audio %s/dir_wr_read/" % test_dir)
runBashFromRoot("chown root:audio %s/dir_wr/" % test_dir)
runBashFromRoot("chown root:audio %s/dir_exec/" % test_dir)
runAnalis2(u_name=user1Name, item='з', p1=1, p2=1, p7=1, p11=1, p12=1)
runAnalis2(u_name=user2Name, item='з', p1=1, p2=1, p7=1, p11=1, p12=1)
print('\n')

print('Пункт и')
runBashFromUser(user_name=user1Name, command="touch /tmp/ivanov.file")
runBashFromUser(user_name=user1Name, command="chmod 1777 /tmp/ivanov.file")
runBashFromRoot("chown " + user1Name + ":audio /tmp/ivanov.file")

print('[user: ' + user2Name + '; action: delete; file: ivanov.file]')
if getCodeRunCommand(u_name=user2Name, command="rm /tmp/ivanov.file") != 0:
    result.append('item: и; user: ' + user2Name + '; action: delete; file: ivanov.file')


print('[user: ' + user1Name + '; action: delete; file: ivanov.file]')
if getCodeRunCommand(u_name=user1Name, command="rm /tmp/ivanov.file") != 1:
    result.append('item: и; user: ' + user1Name + '; action: delete; file: ivanov.file')


# CLEAR
file1 = "/tmp/ivanov.file"
if os.path.isfile(file1):
    os.remove(file1)

shutil.rmtree("%s" % test_dir)


# OUTPUT RESULT
print('\n')
print('РЕЗУЛЬТАТ ТЕСТИРОВАНИЯ')
if len(result) != 0:
    print('при прохождении теста произошли ошибки:')
    for i in result:
        print i
else:
    print('тест пройден успешно')


