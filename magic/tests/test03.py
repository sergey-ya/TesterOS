#!/usr/bin/python
# coding: utf_8

from modules import runTest


testOSF = 'Аудит'
testName = 'Просмотр аудита и ограниченный просмотр аудита'
testNumber = '3'
version = '0.1'
progress = '2/3'


test = runTest(osf=testOSF, name=testName, num=testNumber, ver=version)


try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()
    test.runCmdFirstUser(cmd='cat /var/log/audit/audit.log', out='ok', code=1)
    test.runCmdFirstUser(cmd='cat /var/log/secure', out='ok', code=1)
    test.runCmdFirstUser(cmd='cat /var/log/maillog', out='ok', code=1)
    test.runCmdFirstUser(cmd='cat /var/log/messages', out='ok', code=1)
    # test.runCmdFirstUser(cmd='cat /var/log/iptables', code=1)

    test.runCmdFromRoot(cmd='cat /var/log/audit/audit.log', out='ok', code=0)
    test.runCmdFromRoot(cmd='cat /var/log/secure', out='ok', code=0)
    test.runCmdFromRoot(cmd='cat /var/log/maillog', out='ok', code=0)
    test.runCmdFromRoot(cmd='cat /var/log/messages', out='ok', code=0)
    # test.runCmdFromRoot(cmd='cat /var/log/iptables', code=0)

    test.runCmdFirstUser(cmd='aureport -au', out='ok', code=1)
    test.runCmdFromRoot(cmd='aureport -au', out='ok', code=0)


except Exception as e:
    test.showError(e)


finally:
    # result out--------------------------------------------------------------------------------------------------------
    test.showResultBlock()



