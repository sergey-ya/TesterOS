#!/usr/bin/python
# coding: utf_8


import os

# поиск данных в каталоге
def getDataFolder(folder=None, type=None):
    try:
        out = []
        names = os.listdir(folder)
        for name in names:
            fullname = os.path.join(folder, name)
            if os.path.isfile(fullname):
                if type == 'files' or type == 'all':
                    out.append(name)
            elif os.path.isdir(fullname):
                if type == 'folders' or type == 'all':
                    out.append(name)
        return out
    except:
        return None


# поиск данных в каталоге и формирование в виде дерева
def getTreeDataFolder(folder=None, type=None):
    if folder == '#':
        folder = '/'

    lst = getDataFolder(folder=folder, type='folders')
    dirLst = []

    for i in lst:
        if type == 'folders':
            lst2 = getDataFolder(folder=os.path.join(folder, i), type='folders')
        elif type == 'files':
            lst2 = getDataFolder(folder=os.path.join(folder, i), type='all')

        if lst2 == None:
            pass
        elif len(lst2) == 0:
            dirLst.append(dict(id=os.path.join(folder, i), text=i, children=False, type='root'))
        elif len(lst2) > 0:
            dirLst.append(dict(id=os.path.join(folder, i), text=i, children=True, type='root'))

    dirLst = sorted(dirLst, key=lambda id: id['text'])

    lst = getDataFolder(folder=folder, type='files')
    fileLst = []

    for i in lst:
        fileLst.append(dict(id=os.path.join(folder, i), text=i, type='file'))

    fileLst = sorted(fileLst, key=lambda id: id['text'])

    if type == 'folders':
        return dirLst
    elif type == 'files':
        return dirLst + fileLst


# for i in getTreeDataFolder(folder="#", type='folders'):
#     print i
# print(getDataFolder('/', 'all'))