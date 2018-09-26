#!/usr/bin/env python
# -*- coding: utf-8 -*-

import koji
import dateutil.parser as dp
import os
import createrepo_c as cr
import createrepo
import json
import requests


# *******************************************REPO MANAGER*******************************************
def get_tag_list(stapel_url):
    session = koji.ClientSession(stapel_url + '/kojihub/')
    taglist = session.listTags()
    res = sorted([dict(name=tag['name'], id=tag['id']) for tag in taglist if 'build' not in tag['name']])
    return res


def get_pkgs_by_tag(stapel_url, tag_id):
    # ускорить процесс поиска пакетов со сборками
    #
    #
    session = koji.ClientSession(stapel_url + '/kojihub/')
    pkgList = sorted([pkg for pkg in session.listPackages(tagID=int(tag_id))], key=lambda pkg: pkg['package_name'])
    return pkgList

    # pkgslist = session.listPackages(tag)
    #
    # buildList = session.listBuilds(state=1)
    # res = []
    # for i in pkgslist:
    #     for k in buildList:
    #         if k['package_id'] == i['package_id']:
    #             res.append(dict(name=i['package_name'], id=i['package_id']))
    #             break
    # result = sorted(res, key=lambda res: res['name'])
    # return result


def get_builds_by_tag(stapel_url, pkg_id, tag_id):
    session = koji.ClientSession(stapel_url + '/kojihub/')
    pkg_id = int(pkg_id)
    tag_id = int(tag_id)
    buildsList = session.listBuilds(pkg_id, state=1)

    res = []
    for build in buildsList:
        tagsList = session.listTags(build['build_id'])
        for tag in tagsList:
            if tag['id'] == tag_id:
                res.append(dict(url=stapel_url + '/koji/buildinfo?buildID=' + str(build['build_id']), name=build['name'],
                                nvr=build['nvr'], id=build['build_id'], version=build['version'],
                                release=build['release'], date=parse_time(build['completion_time']),
                                author=build['owner_name'], tags=get_tags_str(stapel_url=stapel_url,
                                                                              build_id=build['build_id'])))

    result = sorted(res, key=lambda res: res['date'], reverse=True)

    return result



def exportRPMS(tag=None, entire=False, Builds=None, url=None, replace=False, repo=None, update=False, sign=False):
    """

    :param tag: tag
    :param Builds: list of maps of builds needed to export:
                package_name: string,
                build_id: build id,
                build_version: build version,
                build_release: build release
    :param url: url of kojihub
    :param replace: replace flag
    :param repo: path to prod repo
    :param update: update flag
    :param sign: sign flag
    :return:
    """
    if (Builds and url and repo) is None:
        raise Exception("Nothing to do!")
    rpms = []
    session = koji.ClientSession("%s/kojihub" % url)
    url_files = "%s/kojifiles" % url
    status = dict(code=0, message="")
    try:
        if tag and entire:
            Builds = session.listTagged('dist-gl7-updates', latest=True)

        for build in Builds:
            rpms.extend(dict(package_name=build['package_name'], nvr=rpm['nvr'], build_version=build['version'],
                             build_release=build['release'], arch=rpm['arch'])
                        for rpm in session.listRPMs(buildID=int(build['build_id'])))
    except Exception as e:
        status = dict(code=1, message="Fail[koji]: %s" % e.message)

    def _chk_path(path):
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except Exception as e:
                global status
                status = dict(code=1, message="Fail[mkdir]: %s" % e.message)

    pkg_count_dict = dict(srpms=0, debug_rpms=0, rpms=0)
    for rpm in rpms:
        rpm_name = "%s.%s.rpm" % (rpm['nvr'], rpm['arch'])
        if rpm['arch'] in ['src']:
            subdir = "source/SRPMS"
            _chk_path("%s/%s" % (repo, subdir))
            pkg_count_dict['srpms'] += 1
        elif 'debuginfo' in rpm['nvr']:
            subdir = "%s/%s" % ("x86_64", "debug")
            _chk_path("%s/%s" % (repo, subdir))
            rpm_path = "%s/%s/%s" % (repo, subdir, rpm_name)
            pkg_count_dict['debug_rpms'] += 1
        elif rpm['arch'] in ['noarch', 'x86_64', 'i686', 'i386']:
            subrepo = ("os", "updates")[update]
            subdir = "%s/%s" % ("x86_64", subrepo)
            _chk_path("%s/%s" % (repo, subdir))
            rpm_path = "%s/%s/%s" % (repo, subdir, rpm_name)
            pkg_count_dict['rpms'] += 1
        try:
            rpm_response = requests.get("%s/packages/%s/%s/%s/%s/%s" % (
                url_files, rpm['package_name'], rpm['build_version'], rpm['build_release'], rpm['arch'], rpm_name))
        except Exception as e:
            status = dict(code=1, message="Fail[getrpm]: %s" % e.message)

        with open("%s/%s/%s" % (repo, subdir, rpm_name), 'w') as rpm_file:
            try:
                rpm_file.write(rpm_response.content)
            except Exception as e:
                status = dict(code=1, message="Fail[writerpm]: %s" % e.message)

        if sign:
            try:
                import pexpect
                import locale

                locale.setlocale(locale.LC_ALL, 'en_US.utf-8')

                env = os.environ
                env['LC_ALL'] = 'C'

                child = pexpect.spawn('rpm', ['--addsign', rpm_path], env=env)
                index = child.expect(['Passphrase: ', pexpect.EOF])
                # print index
                if index == 0:
                    child.sendline('qqqwww')
                    rpm_path = None
                else:
                    child.expect(pexpect.EOF)
                    child.expect(pexpect.EOF)
                    child.close()
                    rpm_path = None
            except Exception as e:
                status = dict(code=1, message="Fail[sign]: %s" % e.message)

        status = dict(code=0, message="Done")

    return dict(status=status, pkg_count=pkg_count_dict)


def genRepoMd(path=None, comps_path=None):
    if not path:
        raise Exception("No path")
    mdconfig = createrepo.MetaDataConfig()
    mdconfig.directory = path
    mdconfig.groupfile = comps_path
    mdgen = createrepo.MetaDataGenerator(mdconfig)
    mdgen.doPkgMetadata()
    mdgen.doRepoMetadata()
    mdgen.doFinalMove()
    return 0






# список пакетов из репозитория
def get_pkgs_from_repo(path_to_repo):
    # path_to_repo = repr(path_to_repo)

    result = []
    md = cr.Metadata()
    md.locate_and_load_xml(path_to_repo)
    for key in md.keys():
        pkg = md.get(key)
        result.append(dict(nvra=pkg.nvra(), name=pkg.name))

    pkgList = sorted(result, key=lambda pkg: pkg['name'])

    return pkgList


# полная информация о пакете
def get_pkg_info(path_to_repo=None, pkg_nvra=None):
    result = {}
    md = cr.Metadata()
    md.locate_and_load_xml(path_to_repo)
    for key in md.keys():
        pkg = md.get(key)
        if pkg.nvra() == pkg_nvra:
            result.update(name=pkg.name)
            result.update(nvra=pkg.nvra())
            result.update(checksumType=pkg.checksum_type)
            result.update(checksum=pkg.pkgId)
            result.update(arch=pkg.arch)
            result.update(version=pkg.version)
            result.update(epoch=pkg.epoch)
            result.update(release=pkg.release)
            result.update(summary=pkg.summary)
            result.update(description=pkg.description)
            result.update(url=pkg.url)
            result.update(timeFile=pkg.time_file)
            result.update(timeBuild=pkg.time_build)
            result.update(license=pkg.rpm_license)
            result.update(vendor=pkg.rpm_vendor)
            result.update(group=pkg.rpm_group)
            result.update(buildhost=pkg.rpm_buildhost)
            result.update(sourceRpm=pkg.rpm_sourcerpm)
            result.update(headerStart=pkg.rpm_header_start)
            result.update(headerEnd=pkg.rpm_header_end)
            result.update(packager=pkg.rpm_packager)
            result.update(sizePackage=pkg.size_package)
            result.update(sizeInstalled=pkg.size_installed)
            result.update(sizeArchive=pkg.size_archive)
            result.update(locationHref=pkg.location_href)
            result.update(locationBase=pkg.location_base)

            requires = []
            for item in pkg.requires:
                requires.append(dict(name=item[cr.PCOR_ENTRY_NAME], flags=item[cr.PCOR_ENTRY_FLAGS],
                                     epoch=item[cr.PCOR_ENTRY_EPOCH], version=item[cr.PCOR_ENTRY_VERSION],
                                     release=item[cr.PCOR_ENTRY_RELEASE], pre=item[cr.PCOR_ENTRY_PRE]))
            result.update(requires=requires)

            provides = []
            for item in pkg.provides:
                provides.append(dict(name=item[cr.PCOR_ENTRY_NAME], flags=item[cr.PCOR_ENTRY_FLAGS],
                                     epoch=item[cr.PCOR_ENTRY_EPOCH], version=item[cr.PCOR_ENTRY_VERSION],
                                     release=item[cr.PCOR_ENTRY_RELEASE]))
            result.update(provides=provides)

            conflicts = []
            for item in pkg.conflicts:
                conflicts.append(dict(name=item[cr.PCOR_ENTRY_NAME], flags=item[cr.PCOR_ENTRY_FLAGS],
                                      epoch=item[cr.PCOR_ENTRY_EPOCH], version=item[cr.PCOR_ENTRY_VERSION],
                                      release=item[cr.PCOR_ENTRY_RELEASE]))
            result.update(conflicts=conflicts)

            obsoletes = []
            for item in pkg.obsoletes:
                conflicts.append(dict(name=item[cr.PCOR_ENTRY_NAME], flags=item[cr.PCOR_ENTRY_FLAGS],
                                      epoch=item[cr.PCOR_ENTRY_EPOCH], version=item[cr.PCOR_ENTRY_VERSION],
                                      release=item[cr.PCOR_ENTRY_RELEASE]))
            result.update(conflicts=obsoletes)

            files = []
            for item in pkg.files:
                files.append(dict(name=item[cr.FILE_ENTRY_NAME], path=item[cr.FILE_ENTRY_PATH],
                                  type=item[cr.FILE_ENTRY_TYPE]))
            result.update(files=files)

            changelogs = []
            for item in pkg.changelogs:
                changelogs.append(dict(author=item[cr.CHANGELOG_ENTRY_AUTHOR], date=item[cr.CHANGELOG_ENTRY_DATE],
                                  changelog=item[cr.CHANGELOG_ENTRY_CHANGELOG]))
            result.update(changelogs=changelogs)




    return result


# print(get_pkg_info('/home/yarikov/web/test-repo', '389-ds-base'))






def getPkgLst(stapelUrl=None):
    # ускорить процесс поиска пакетов со сборками
    #
    #
    session = koji.ClientSession(stapelUrl + '/kojihub')
    pkgslist = session.listPackages()

    # buildList = session.listBuilds(state=1)
    res = []
    # for i in pkgslist:
    #     for k in buildList:
    #         if k['package_id'] == i['package_id']:
    #             res.append(dict(name=i['package_name'], id=i['package_id']))
    #             break
    for i in pkgslist:
        res.append(dict(name=i['package_name'], id=i['package_id']))

    result = sorted(res, key=lambda res: res['name'])
    return result


def parse_time(time):
    parsed_t = dp.parse(time)
    return parsed_t.strftime('%Y-%m-%d %H:%M:%S')


def get_tags_str(stapel_url=None, build_id=None):
    build_id = int(build_id)
    session = koji.ClientSession(stapel_url + '/kojihub')
    tagslist = session.listTags(build_id)
    tags = sorted([dict(name=tag['name'], id=tag['id']) for tag in tagslist], key=lambda res: res['name'])
    # tags = []
    # for tag in tagslist:
    #     tags.append('<p>' + tag['name'] + '</p>')
    # res = ''.join(tags)
    return tags


def getBuildLst(stapelUrl=None, pkgId=None):
    session = koji.ClientSession(stapelUrl + '/kojihub')
    buildLst = session.listBuilds(int(pkgId), state=1)
    # epoch

    # for i in buildslist:
    #     print(i)

    # print(koji.get_tags(5963))

    res = sorted([dict(url=stapelUrl + '/koji/buildinfo?buildID=' + str(build['build_id']), version=build['version'],
                       release=build['release'], build_id=build['build_id'],
                       date=parse_time(build['completion_time']),
                       author=build['owner_name'],
                       tags=get_tags_str(stapel_url=stapelUrl, build_id=build['build_id']))
                  for build in buildLst], key=lambda res: res['date'], reverse=True)
    return res



# ГЕНЕРАЦИЯ ФАЙЛА УСТАНОВКИ ПАКЕТА СОС ТАПЕЛЯ
def generateFileinst(dir=None, stapel_url=None, build_id=None):

    def get_build_tags(stapel_url=None, build_id=None):
        build_id = int(build_id)
        session = koji.ClientSession(stapel_url + '/kojihub')
        tagslist = session.listTags(build_id)
        res = sorted([dict(name=tag['name'], id=tag['id']) for tag in tagslist], key=lambda res: res['name'])
        return res

    def get_build_name(stapel_url=None, build_id=None):
        build_id = int(build_id)
        session = koji.ClientSession(stapel_url + '/kojihub')
        build = session.getBuild(build_id)
        return build['package_name']

    def gen_fileinst_content(index=None, url=None, tag=None):
        index = str(index)
        tag = str(tag)

        if tag.find("i686") != -1:
            arch = "i386"
        else:
            arch = "x86_64"

        con = []
        con.append("file_repo" + index + "='/etc/yum.repos.d/Koji-" + tag + ".repo'")
        con.append("touch $file_repo" + index)
        con.append("echo -n > $file_repo" + index)
        con.append("echo '[koji-" + tag + "]' >> $file_repo" + index)
        con.append("echo 'name=Koji-" + tag + " - Stapel' >> $file_repo" + index)
        con.append("echo 'baseurl=" + url + "/kojifiles/repos/" + tag + "-build/latest/" + arch + "/' >> $file_repo" + index)
        con.append("echo 'enabled=1' >> $file_repo" + index)
        con.append("echo 'gpgcheck=0' >> $file_repo" + index)
        con.append("")
        result = "\n".join(con)
        return result


    build_tags = get_build_tags(stapel_url=stapel_url, build_id=build_id)

    if not build_tags:
        raise Exception("Не найдены теги")

    build_name = get_build_name(stapel_url=stapel_url, build_id=build_id)

    file_name = 'install_' + build_name + '_from_koji.sh'
    file_path = dir + '/' + file_name

    file = open(file_path, 'w')

    file.write('#!/bin/bash\n')

    for index, tag in enumerate(build_tags):
        file.write(gen_fileinst_content(index=index, url=stapel_url, tag=tag['name']))

    file.write('command="yum clean all"\n')
    file.write('eval $command\n')
    file.write('command="yum install -y ' + build_name + '"\n')
    file.write('eval $command\n')

    for index, tag in enumerate(build_tags):
        file.write('rm $file_repo' + str(index) + '\n')

    file.close()

    return file_name





# res = get_pkgs()
# print(len(res))

# for i in get_builds(810):
#     print(i)

# generate_file(5762)



# выбираем из сборок с id 5963
# tag = koji.get_tags(5963)
# print koji.generate_repo_file(2363)

# 2363 без тегов




