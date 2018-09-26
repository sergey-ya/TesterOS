#!/usr/bin/python
# coding: utf_8


import paramiko




class runTesting(object):

    sshClient = None
    result = None

    def runCmd(self, cmd=None):
        stdin, stdout, stderr = self.sshClient.exec_command(cmd)
        output = stdout.read().rstrip()
        error = stderr.read().rstrip()
        returnCode = stdout.channel.recv_exit_status()

        return dict(output=output, error=error, code=returnCode)



    def start(self):
        import os
        # return self.runCmd("sudo -S python " + os.path.join(os.getcwd(), 'tests/test03.py'))

        # ssh = paramiko.SSHClient()
        # ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        # ssh.connect(server, username=username, password=password)
        sftp = self.sshClient.open_sftp()
        sftp.put('/home/yarikov/mnt/comps.xml', '/home/user/comps.xml')
        sftp.close()

        # return os.path.join(os.getcwd(), 'tests')





    def __init__(self, host=None, rootPas=None):
        self.sshClient = paramiko.SSHClient()
        self.sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sshClient.connect(hostname=host, username='root', password=rootPas, port=22)

        self.result = self.start()

        self.sshClient.close()




print(runTesting(host='10.81.81.162', rootPas='qqqwww').result)




