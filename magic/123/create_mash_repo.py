#!/usr/bin/env python

import sys
import os
import glob
import koji
import requests
import time
import string
import sys, getopt
import re
import createrepo
import rpm
from termcolor import colored
from subprocess import call

class ArgError(Exception):
    def __init__(self, value, message):
        self.value = value
        self.message = message
        
class TagError(Exception):
    def __init__(self, tag, url, message):
        self.tag = tag
        self.url = url
        self.message = message
        
class PathError(Exception):
    def __init__(self, path, message):
        self.path = path
        self.message = message

class PkgsError(Exception):
    def __init__(self, message):
        self.message = message


class Arguments:
    def __init__(self, argv):
        self.arch = "x86_64"
        self.output_dir = os.getcwd()
        self.kojirepos = []
        self.delta = False
        self.sign = False
        self.packages = []
        self.replace = False
        try:
            opts, args = getopt.getopt(argv,'rdho:k:n:sl:',['output=','kojirepo=','package-list='])
        except getopt.GetoptError:
            print Usage()
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print Usage()
                sys.exit(1)
            elif opt in ['-k', '--kojirepo']:
                try:
                    kojirepo = self.ParseKojiHubArg(arg)
                    self.addUrl(kojirepo['url'])
                    self.checkTag(kojirepo['url'],kojirepo['tag'])
                    self.kojirepos.append(kojirepo)
                except (ArgError,TagError) as e:
                    print "Error %s" % e.message
                    sys.exit(2)
            elif opt in ['-s']:
                self.sign = True
            elif opt in ['-d']:
                self.delta = True
            elif opt in ['-r']:
                self.replace = True
            elif opt in ['-o','--output']:
                try:
                    self.addPath(arg)
                except PathError as e:
                    print "Error %s" % e.message
                    sys.exit(2)
            elif opt in ['-l','--package-list']:
                self.packages = self.ParsePackagesList(arg)
        if not opts:
            print Usage()
            sys.exit(2)
            
    def addPath(self, path):
        if not os.path.exists(path):
            raise PathError(path ,'\"%s\" path does not exist' % colored(path, 'red'))
        self.output_dir = path

    def addUrl(self,url):
        re_url=re.compile(r'http[s]?://[0-9a-zA-Z\-\./]+/kojihub')
        if re_url.match(url):
            return True
        else:
            raise ArgError(url,'%s is not valid kojihub URL' % colored(url,"yellow"))
            return False

    def checkTag(self,url, tag):
        session = koji.ClientSession(url)
        tags = session.listTags()
        ok = False
        for _tag in tags:
            if tag == _tag['name']:
                ok = True
                break
        if not ok:
            raise TagError(tag, url, "Tag %s is not valid for %s url" % (colored(tag,"red"), colored(url,"yellow")))

    def ParseKojiHubArg(self,arg):
        kojihub_replace = re.compile(r'kojihub')
        result = {}
        args = arg.split(",")
        if len(args) != 2:
            raise ArgError(args,'kojirepo: Expected 2 args, but given %d' % len(args))
        result['tag'] = args[0]
        result['url'] = args[1]
        result['files'] = kojihub_replace.sub('kojifiles', result['url'])
        return result
    
    def ParsePackagesList(self,arg):
        result = []
        pkgs=arg.split(",")
        if len(pkgs) != 0:
            for pkg in pkgs:
                result.append({'package_name': pkg})
        else:
            raise PkgsError('Expected at least one package')
        return result
        
def Usage():
    return "Usage: -k <tag1>,<URL for kojihub 1> [-k <tagN>,<URL for kojihub N>...] [-n] [-l <packages, separated by semicolon>] -o <Outputdir>"
        
def _chk_path(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)
def main():
    debug_info = re.compile(r'.*debuginfo.*')
    ignore = []
    args = Arguments(sys.argv[1:])
    with open("to_sign", "w") as new:
        for kojirepo in args.kojirepos:
            session = koji.ClientSession(kojirepo['url'])
            packages = args.packages or  session.listPackages() #kojirepo['tag'])
            for pkg in packages:
                if pkg['package_name'] in ignore:
                    continue
                rpmList = session.getLatestRPMS(kojirepo['tag'],package=pkg['package_name'])
                ignore.append(pkg['package_name'])
                #if rpmList[1]['tag_name'] != kojirepo['tag']: 
                #    continue 
                try:
                    if rpmList[1][0]['tag_name'] != kojirepo['tag']:
                        continue
                except IndexError as e:
                    pass
                for rpm in rpmList[0]:
                    rpm_name = "%s-%s-%s.%s.rpm" % (rpm['name'], rpm['version'], rpm['release'], rpm['arch'])
                    print rpm
                    if rpm['arch'] in ['src']:
                        repo_dir = "source/SRPMS"
                        _chk_path("%s/%s" % (args.output_dir, repo_dir))
                    elif debug_info.match(rpm['name']):
                        print "Found Debuginfo"
                        repo_dir = "%s/%s" % (args.arch, "debug")
                        _chk_path("%s/%s" % (args.output_dir, repo_dir))
                        rpm_path = "%s/%s/%s" % (args.output_dir, repo_dir, rpm_name)
                    elif rpm['arch'] in ['noarch', 'x86_64', 'i686', 'i386']:
                        repo_dir = "%s/%s" % (args.arch, "os")
                        _chk_path("%s/%s" % (args.output_dir, repo_dir))
                        rpm_path = "%s/%s/%s" % (args.output_dir, repo_dir, rpm_name)
                    build = session.getBuild(rpm['build_id'])
                    rpm_response = requests.get("%s/packages/%s/%s/%s/%s/%s" % (kojirepo['files'], pkg['package_name'], build['version'], build['release'], rpm['arch'], rpm_name))
                    if os.path.exists("%s/%s/%s" % (args.output_dir, repo_dir, rpm_name)) and args.delta:
                        continue
                    rpm_old_glob = glob.glob("%s/%s/%s-[0-9]*.%s.rpm" % (args.output_dir, repo_dir, rpm['name'], rpm['arch']))
                    if args.replace:
                        try:
                            [os.remove("%s" % (rpm_old)) for rpm_old in rpm_old_glob]
                        except:
                            pass
                    rpm_old_glob = []
                    with open("%s/%s/%s" % (args.output_dir, repo_dir, rpm_name), 'w') as rpm_file:
                        rpm_file.write(rpm_response.content)
                    if rpm_path is not None:
                        new.write("%s\n" % rpm_path)
                        if args.sign:
                            call(["rpm","--addsign",rpm_path],stdout=None,stderr=None)
                        rpm_path = None

if __name__ == '__main__':
    main()