#!/usr/bin/python
# coding: utf_8

import os, shutil, pwd, sys
from datetime import datetime
import time
from modules import runTest
import socket
import modules as tm
import collections


testOSF = 'Аудит'
testName = 'Сигналы нарушения безопасности'
testNumber = '1'
version = '0.1'
progress = '3/3'

params = ['firstUser']
test = runTest(osf=testOSF, name=testName, num=testNumber, ver=version, params=params)
firstUser = test.params['firstUser']

file1 = '/etc/sudoers'

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()
    test.runCmdFromRoot(cmd="cp %s %s2" % (file1, file1), out='ok', code=0)


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()
    text = []
    text.append('Defaults mailto="root@localhost.localdomain"')
    text.append('Defaults mail_badpass')
    text.append('Defaults mail_no_perms')
    text.append('Defaults mail_no_user')
    text.append('Defaults mail_always')
    tm.addRowToFile(file=file1, text=text)
    test.showActionMsg('add data to file %s' % file1)


    test.runCmdFirstUser(cmd='sudo su', out='ok', code=1)
    time.sleep(3)

    f = open('/var/spool/mail/root', "r+")
    rows = f.readlines()
    f.close()

    today = datetime.today()
    status = False
    for row in rows:
        row = row.replace(' ', '')
        findText1 = socket.gethostname() + ' : ' + today.strftime("%b %-d %H:")
        findText1 = findText1.replace(' ', '')
        findText2 = '%s:%sNOTinsudoers' % (firstUser, firstUser)
        findText3 = 'COMMAND=/bin/su'

        if row.find(findText1) == 0:
            if row.find(findText2) > 0:
                if row.find(findText3) > 0:
                    status = True

    if not status:
        test.addResult(msg='Не найдено извещение о нарушении информационной безопасности.',
                       wait='param1:%s, param2:%s, param3:%s' % (findText1, findText2, findText3),
                       taken='file /var/spool/mail/root')


except Exception as e:
    test.showError(e)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()
        test.runCmdFromRoot(cmd='cp %s2 %s' % (file1, file1), out='ok', code=0, remov=True)
        test.runCmdFromRoot(cmd='rm %s2' % file1, out='ok', code=0, remov=True)

    except Exception as e:
        test.showError(e)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()
