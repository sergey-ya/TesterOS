#!/usr/bin/python
# coding: utf_8

import os

magicFolder = '/home/yarikov/web/testeros/magic'
workFolder = os.path.join(magicFolder, 'work')

msettings = {
    'MAGIC_FOLDER': magicFolder,
    'WORK_FOLDER': workFolder,
    'BUILD_ISO': {
        'PATH': os.path.join(workFolder, 'buildiso'),
        'CONFIG_FILE': os.path.join(workFolder, 'buildiso/config.file'),
    }
}
# print(msettings['BUILD_ISO']['ACTIONS_LOG'])