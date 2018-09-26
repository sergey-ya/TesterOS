#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse, Http404
from django.utils import timezone

from .models import ObjectSf, Tests, Testing, TestJournal, Settings, ActionLog, UserProfile, BuildIsoSettings
from .models import BuildIso_Log

from .forms import PassingTestCaseForm

import ntpath, datetime, json, sys, os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import ssl
from magic.buildiso import executeBuildIso

import datetime


# -----------
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
import dateutil.parser as dp
from django.http import JsonResponse



from magic.isocompare2 import compareIso, searchPkgOnIso, getIsoLst
import magic.kojirepo as repo
from magic.parsetest import parseTestFile
from magic.vulnersscanner import runScanner


def ajax_view(request):
    try:
        if request.method == 'POST':
            action = request.POST.get('action')

            # сравнение iso образов
            if action == 'compareIso':
                return render_to_response('testeros/isocompare/ajax_result.html', {
                    'result': compareIso(iso1_path=request.POST.get('iso1'), iso2_path=request.POST.get('iso2'))
                })


            # поиск пакетов на iso образе
            if action == 'searchPkg':
                return render_to_response('testeros/packages/ajax_result.html', {
                    'result': searchPkgOnIso(iso_path=request.POST.get('iso'), pkg_mask=request.POST.get('mask')),
                })

            # ********************************STAPEL IP***********************************
            # ****************************************************************************
            # получение списка пакетов со стапеля
            if action == 'getPkgLst':
                return HttpResponse(json.dumps(repo.getPkgLst(request.POST.get('stapelUrl'))),
                                    content_type='application/json')

            # список сборок для пакета
            if action == 'getBuildLst':
                return HttpResponse(json.dumps(repo.getBuildLst(stapelUrl=request.POST.get('stapelUrl'),
                                                                pkgId=request.POST.get('pkgId'))),
                                    content_type='application/json')

            # генерация файла для установки пакета
            if action == 'genRepoFile':
                import os
                file_path = os.path.join('/home/yarikov/upload', repo.generateFileinst(
                    dir='/home/yarikov/upload', stapel_url=request.POST.get('url'),
                    build_id=request.POST.get('build_id')))
                return HttpResponse(file_path, content_type='text/html')


            # ********************************TESTCASE************************************
            # ****************************************************************************
            # получаем информацио тесте
            if action == 'getTestInfo':
                import os
                testInfo = parseTestFile(os.path.join(os.getcwd(), request.POST.get('testFile1')))
                return render_to_response('testeros/tests/ajax-testinfo.html', {'result': testInfo,
                                                                                'testFile2': request.POST.get('testFile2')})

            # скачиваем файл теста
            if action == 'getTestFile':
                file_path = '/home/yarikov/web/testeros/apps/' + request.POST.get('testFile')
                return HttpResponse(file_path, content_type='text/html')



            # получаем информацию о тестировании
            if action == 'getTestingInfo':
                objectSf = ObjectSf.objects.all()
                tests = Tests.objects.all()
                objectSf_list = list(objectSf)
                tests_list = list(tests)

                result = []

                for osf in objectSf_list:
                    tests = []
                    for test in tests_list:
                        if test.object_sf_num == osf.serial_num:
                            tests.append(dict(id=test.id, num=test.serial_num, name=test.name, file1=test.file1,
                                              file2=test.file2))

                    result.append(dict(num=osf.serial_num, name=osf.name, tests=tests))

                testingId = request.POST.get('id', '')

                for i in result:
                    for k in i['tests']:
                        testInfo = TestJournal.objects.filter(testing_id=testingId, test_id=k['id']).values()
                        if testInfo:
                            k.update(begin_date=testInfo[0]['begin_date'], end_date=testInfo[0]['end_date'],
                                     comment=testInfo[0]['comment'], status=testInfo[0]['status'],
                                     journal_id=testInfo[0]['id'])
                            # print(testInfo[0]['begin_date'])
                        else:
                            # если не найдено теста в журнале
                            pass

                # for i in result:
                #     print(i)


                result = sorted(result, key=lambda x: x['num'])

                for res in result:
                    res['tests'] = sorted(res['tests'], key=lambda x: x['num'])



                # id = request.POST.get('id', '')
                # testingInfo = TestJournal.objects.filter(testing_id=id)


                return render_to_response('testeros/testing/ajax-journal.html', {'result': result})
                # data = serializers.serialize('json', testingInfo)
                # return HttpResponse(data, content_type='application/json')

            # смена статуса у теста
            if action == 'editTestStatus':
                journalId = request.POST.get('testId')
                status = request.POST.get('status')
                status = int(status)

                now = datetime.datetime.now(tz=timezone.utc)
                if status == 4 or status == 3 or status == 2:
                    TestJournal.objects.filter(id=journalId).update(end_date=now, status=status)
                elif status == 1:
                    TestJournal.objects.filter(id=journalId).update(begin_date=now, end_date=None, status=1)

                # проверка на состояние тестов в журнале для статуса тестирования
                testJournal = TestJournal.objects.filter(id=journalId).values()
                testJournals = TestJournal.objects.filter(testing_id=testJournal[0]['testing_id']).values()

                status0 = 0
                status1 = 0
                status2 = 0
                status3 = 0
                status4 = 0
                for i in testJournals:
                    if i['status'] == 0:
                        status0 += 1
                    if i['status'] == 1:
                        status1 += 1
                    if i['status'] == 2:
                        status2 += 1
                    if i['status'] == 3:
                        status3 += 1
                    if i['status'] == 4:
                        status4 += 1

                if status0 == 0 and status1 == 0 and status3 == 0:
                    # print('set status пройден')
                    Testing.objects.filter(id=testJournal[0]['testing_id']).update(status=3)
                elif status0 == 0 and status1 == 0:
                    Testing.objects.filter(id=testJournal[0]['testing_id']).update(status=2)
                else:
                    Testing.objects.filter(id=testJournal[0]['testing_id']).update(status=0)


                return HttpResponse('ok', content_type='text/html')

            # сохранение комментария
            if action == 'saveComment':
                journalId = request.POST.get('testId')
                text = request.POST.get('text')

                if TestJournal.objects.filter(id=journalId).update(comment=text) == 1:
                    return HttpResponse('ok', content_type='text/html')
                else:
                    raise Exception('Не удалось сохранить комментарий.')



            # ********************************REPO****************************************
            # ********************************REPO MANAGER********************************
            # ****************************************************************************
            # получить список тегов со стапеля
            if action == 'getTagList':
                try:
                    data = repo.get_tag_list(request.POST.get('stapel_url', ''))
                    jsond = json.dumps(data)
                    return HttpResponse(jsond, content_type='application/json')
                except:
                    raise Exception('Невозможно загрузить список тегов.')

            # получить список пакетов со стапеля по тегу
            if action == 'getPkgsByTag':
                data = repo.get_pkgs_by_tag(request.POST.get('stapel_url'), request.POST.get('tag_id'))
                jsond = json.dumps(data)
                return HttpResponse(jsond, content_type='application/json')

            # получить список сборок со стапеля для пакета по тегу
            if action == 'getBuildsByTag':
                data = repo.get_builds_by_tag(request.POST.get('stapel_url'), request.POST.get('pkg_id'),
                                              request.POST.get('tag_id'))
                jsond = json.dumps(data)
                return HttpResponse(jsond, content_type='application/json')

            # экспорт пакетов
            if action == 'exportRPMS':
                now = datetime.datetime.now(tz=timezone.utc)
                stapel = request.POST.get('stapel_url')
                repoUrl = request.POST.get('repo')
                tag = request.POST.get('tag')
                builds = request.POST.get('builds')
                buildLst = json.loads(request.POST.get('builds'))
                entire = False
                replace = json.loads(request.POST.get('replace'))
                update = json.loads(request.POST.get('update'))
                sign = json.loads(request.POST.get('sign'))

                data = repo.exportRPMS(url=stapel, repo=repoUrl, tag=tag, Builds=buildLst, entire=entire, replace=replace,
                                       update=update, sign=sign)



                # compas_path = '/home/yarikov/web/test/redos/comps.xml'
                # if update:
                #     path = repoUrl + '/x86_64/updates'
                # else:
                #     path = repoUrl + '/x86_64/os'
                # repo.genRepoMd(path=path, comps_path=compas_path)
                #


                status = data['status']['code']
                msg = data['status']['message']

                # print(builds)
                actionLog = ActionLog(created_at=now, user_name='testUser', status=status,
                                      message=msg, stapel=stapel, repo=repoUrl, tag=tag,
                                      packages=builds,
                                      entire=entire, replace=replace, update=update, sign=sign)
                actionLog.save()

                if status == 0:
                    return HttpResponse('ok', content_type='text/html')
                else:
                    raise Exception(msg)


            # ********************************REPO STATISTIC******************************
            # ****************************************************************************
            # получить список пакетов из репозитория
            if action == 'getPkgsFromRepo':
                data = repo.get_pkgs_from_repo(request.POST.get('repo_url'))
                jsond = json.dumps(data)
                return HttpResponse(jsond, content_type='application/json')

            # получить информацию о пакете
            if action == 'getPkgInfo':
                data = repo.get_pkg_info(path_to_repo=request.POST.get('repo_url'), pkg_nvra=request.POST.get('pkg_name'))
                jsond = json.dumps(data)
                return HttpResponse(jsond, content_type='application/json')

            # / mnt / pub / Temp / GosLinux2
            # / mnt / pub / Temp / RedOS2



            # ****************************************************************************
            # ********************************BUILDISO************************************
            # ****************************************************************************
            # добавить настройки
            if action == 'addSettingBuildISo':
                buildisoSettings = BuildIsoSettings(name=request.POST.get('name'), comment=request.POST.get('comment'),
                                                    pkgset_repos='[]')
                buildisoSettings.save()

                if buildisoSettings.id:
                    return HttpResponse(buildisoSettings.id, content_type='text/html')
                else:
                    raise Exception('Не удалось сохранить изменения.')

            # удалить настройки
            if action == 'delSettingBuildISo':
                BuildIsoSettings.objects.filter(id=request.POST.get('settingId')).delete()
                return HttpResponse('ok', content_type='text/html')

            # редактировать настройки
            if action == 'editSettingBuildISo':
                settingId = request.POST.get('settingId')
                name = request.POST.get('name')
                comment = request.POST.get('comment')

                if BuildIsoSettings.objects.filter(id=settingId).update(name=name, comment=comment) == 1:
                    return HttpResponse('ok', content_type='text/html')
                else:
                    raise Exception('Не удалось сохранить изменения.')

            # получить настройки для сборки iso
            if action == 'getSettingsBuildISo':
                data = BuildIsoSettings.objects.filter(id=request.POST.get('settingId')).values()
                return JsonResponse({'results': list(data), 'pkgset': json.loads(data[0]['pkgset_repos'])})

            # сохранить настройки
            if action == 'saveSettingBuildISo':
                settingId = request.POST.get('settingId')
                if BuildIsoSettings.objects.filter(id=settingId).update(dir=request.POST.get('dir'),
                                                                        label=request.POST.get('label'),
                                                                        rel_name=request.POST.get('relName'),
                                                                        rel_short_name=request.POST.get('relShortName'),
                                                                        rel_ver=request.POST.get('relVer'),
                                                                        comps_file_path=request.POST.get('compsFilePath'),
                                                                        var_file_path=request.POST.get('varFilePath'),
                                                                        pkgset_repos=request.POST.get('pkgsetRepos')) == 1:
                    return HttpResponse('ok', content_type='text/html')
                else:
                    raise Exception('Не удалось сохранить изменения.')


            # проверка параметров для запуска сборки
            if action == 'checkParamsBuildIso':
                from magic.buildiso import checkParams
                settings = BuildIsoSettings.objects.filter(id=request.POST.get('settingId')).values()

                checkParams(targetDir=settings[0]['dir'], label=settings[0]['label'], relName=settings[0]['rel_name'],
                            relShort=settings[0]['rel_short_name'], relVer=settings[0]['rel_ver'],
                            compsFile=settings[0]['comps_file_path'], varFile=settings[0]['var_file_path'],
                            pkgsetRepos=json.loads(settings[0]['pkgset_repos']))

                return HttpResponse('ok', content_type='text/html')

            # добавляем запись в лог
            if action == 'addLogBuildIso':
                new = BuildIso_Log(user_id=request.user.id, status=1)
                new.save()
                return HttpResponse(new.id, content_type='text/html')

            # запуск сборку образа
            if action == 'runBuildIso':
                try:
                    settings = BuildIsoSettings.objects.filter(id=request.POST.get('settingId')).values()
                    buildIso = executeBuildIso(id=request.POST.get('id'), targetDir=settings[0]['dir'],
                                               label=settings[0]['label'], relName=settings[0]['rel_name'],
                                               relShort=settings[0]['rel_short_name'], relVer=settings[0]['rel_ver'],
                                               compsFile=settings[0]['comps_file_path'], varFile=settings[0]['var_file_path'],
                                               pkgsetRepos=json.loads(settings[0]['pkgset_repos']))

                    now = datetime.datetime.now(tz=timezone.utc)
                    if buildIso.res == 'cancel':
                        BuildIso_Log.objects.filter(id=request.POST.get('id')).update(status=2,
                                                                                      inform='[Canceled] ' + now.strftime("%d-%m-%Y %H:%m"))

                    elif buildIso.res == 'ok':
                        BuildIso_Log.objects.filter(id=request.POST.get('id')).update(close_at=now, status=0,
                                                                                      inform='[Completed] ' + settings[0]['dir'])

                except Exception as e:
                    BuildIso_Log.objects.filter(id=request.POST.get('id')).update(status=3, inform=e)
                    raise Exception(e)

                return HttpResponse(buildIso.res, content_type='text/html')




            # получаем информацию о ходе выполнения сборки
            if action == 'getBuildIsoInfo':
                from magic.buildiso import getActionLog
                jsond = json.dumps(getActionLog(id=request.POST.get('id')))
                return HttpResponse(jsond, content_type='application/json')

            # отменяем запущенную сборку
            if action == 'cancelBuildIso':
                from magic.buildiso import cancelBuildIso
                return HttpResponse(cancelBuildIso(id=request.POST.get('id')), content_type='text/html')


            # получаем статус
            if action == 'getBuildIsoStatus':
                status = BuildIso_Log.objects.filter(id=request.POST.get('id')).values('status')
                jsond = json.dumps(status[0])
                # jsond = json.dumps(status[0], indent=4, sort_keys=True, default=str)
                return HttpResponse(jsond, content_type='application/json')



            # ********************************CATALOG DIALOG********************************
            if action == 'getCatalogDialog':
                from magic.cd import getTreeDataFolder
                data = getTreeDataFolder(folder=request.POST.get('path'), type=request.POST.get('type'))
                jsond = json.dumps(data)
                return HttpResponse(jsond, content_type='application/json')




            # ********************************SETTINGS********************************
            # сохраняем общие настройки
            if action == 'saveSettings':
                iso_gl_path = request.POST.get('iso_gl_path')
                iso_ro_path = request.POST.get('iso_ro_path')

                if Settings.objects.filter(id=1).update(path_to_gl_iso=iso_gl_path, path_to_ro_iso=iso_ro_path, ) == 1:
                    return HttpResponse('ok', content_type='text/html')
                else:
                    raise Exception('Не удалось сохранить настройки.')

            # сохраняем список стапелей
            if action == 'saveStapelLst':
                stapelLst = request.POST.get('stapelLst')
                if Settings.objects.filter(id=1).update(stapel=stapelLst) == 1:
                    return HttpResponse('ok', content_type='text/html')
                else:
                    raise Exception('Не удалось сохранить список стапелей.')

            # сохраняем список репозиториев
            if action == 'saveRepoLst':
                import os
                repoLst = request.POST.get('repoLst')
                # print(repoLst)
                # проверка путей нужна или нет???
                # repos = json.loads(repoLst)
                # for elem in repos:
                #     print os.path.exists(elem['url'])

                if Settings.objects.filter(id=1).update(repo=repoLst) == 1:
                    return HttpResponse('ok', content_type='text/html')
                else:
                    raise Exception('Не удалось сохранить список репозиториев.')



            # сохранение заметки
            if action == 'saveNote':
                if UserProfile.objects.filter(username=request.POST.get('userName')).update(note=request.POST.get('text')) == 1:
                    return HttpResponse('ok', content_type='text/html')

            # загрузка заметки
            if action == 'loadNote':
                userProfile = UserProfile.objects.filter(username=request.POST.get('userName')).values()
                return HttpResponse(userProfile[0]['note'], content_type='text/html')            # загрузка заметки


            # ****************************************************************************
            # ********************************SCANNER*************************************
            # ****************************************************************************
            # сканирование на уязвимости
            if action == 'getVulners':
                result = runScanner(isoPath=request.POST.get('isoPath'), pkgsName=request.POST.getlist('pkgsName[]'),
                                    pkgsNVRA=request.POST.getlist('pkgsNVRA[]'))

                return render_to_response('testeros/scanner/ajax_result.html', {'result': result})


            # ****************************************************************************
            # ********************************TESTING*************************************
            # ****************************************************************************
            # запуск тестирования
            if action == 'runTesting':
                from magic.testing import runTesting

                result = runTesting(host=request.POST.get('host'), rootPas=request.POST.get('rootPas'))

                return render_to_response('testeros/tests/ajax_result.html', {'result': result})





        else:
            data = {'no': 'no'}
            jsond = json.dumps(data)
            return HttpResponse(jsond, content_type='application/json')
    except Exception as e:
        return HttpResponse(Exception(e), status=400)



def ninja(request, key):
    if key == 'qqqwww':
        redirect(home())
    # else:
    #     redirect(login_view())



def login_view(request):

    if request.META['SSL_CLIENT_VERIFY'] == 'SUCCESS':

        clientName = request.META['SSL_CLIENT_S_DN_CN']
        try:
            clientEmail = request.META['SSL_CLIENT_S_DN_Email']
        except:
            clientEmail = request.META['SSL_CLIENT_S_DN_CN']

        user = User.objects.filter(username=clientName)
        if not user:
            User.objects.create_user(username=clientName, email=clientEmail, password='123456')
            UserProfile.objects.create(username=clientName)

        user = authenticate(username=clientName, password='123456')
        if user is not None:
            if user.is_active:
                login(request, user)
                return render(request, 'testeros/home.html', {})
                # return redirect('%s?next=%s' % ('home', request.path))
            else:
                return render(request, 'testeros/home.html', {'result': 'no active'})
        else:
            return render(request, 'testeros/home.html', {'result': 'no auth'})
    else:
        return render(request, 'testeros/home.html', {'result': 'error'})


def logout_view(request):
    logout(request)
    return render(request, 'testeros/home.html', {})


def home(request):
    return render(request, 'testeros/home.html', {})


def isocompare(request):
    settings = Settings.objects.all().values()
    return render(request, 'testeros/isocompare/start.html', {'gllist': getIsoLst(settings[0]['path_to_gl_iso']),
                                                              'rolist': getIsoLst(settings[0]['path_to_ro_iso'])})


def packages(request):
    settings = Settings.objects.all().values()
    return render(request, 'testeros/packages/start.html', {'gllist': getIsoLst(settings[0]['path_to_gl_iso']),
                                                            'rolist': getIsoLst(settings[0]['path_to_ro_iso'])})


def stapelip(request):
    settings = Settings.objects.all().values()
    return render(request, 'testeros/stapelip/start.html', {'stapelLst': json.loads(settings[0]['stapel'])})


def download(request):
    file_path = request.GET.get('filepath')

    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404("Poll does not exist")

    # raise handler404 = 'mysite.views.my_custom_page_not_found_view'
    # сделать нормальное отображение ошибки 404



def tests(request):
    objectSf = ObjectSf.objects.all()
    tests = Tests.objects.all()
    objectSf_list = list(objectSf)
    tests_list = list(tests)

    result = []

    for osf in objectSf_list:
        tests = []
        for test in tests_list:
            if test.object_sf_num == osf.serial_num:
                tests.append(dict(id=test.serial_num, name=test.name, file1=test.file1, file2=test.file2))

        result.append(dict(id=osf.serial_num, name=osf.name, tests=tests))

    result = sorted(result, key=lambda x: x['id'])

    for res in result:
        res['tests'] = sorted(res['tests'], key=lambda x: x['id'])

    return render(request, 'testeros/tests/start.html', {'tests': result})


def scanner(request):
    settings = Settings.objects.all().values()
    return render(request, 'testeros/scanner/start.html', {'gllist': getIsoLst(settings[0]['path_to_gl_iso']),
                                                            'rolist': getIsoLst(settings[0]['path_to_ro_iso'])})


@login_required
def testing(request):

    if request.method == "POST":
        form = PassingTestCaseForm(request.POST)
        if form.is_valid():
            now = datetime.datetime.now(tz=timezone.utc)
            post = form.save(commit=False)
            post.begin_date = now
            post.status = 0
            post.save()

            tests = Tests.objects.all()
            tests_list = list(tests)
            for test in tests_list:
                TestJournal.objects.create(testing_id=post.id, test_id=test.id, status=0)

            return redirect('testing')
    else:
        testing = Testing.objects.all()
        testing_list = list(testing)
        form = PassingTestCaseForm()

        return render(request, 'testeros/testing/start.html', {'testing': testing_list, 'form': form})


@login_required
def testing_test(request, journal_id):

    testjournal = TestJournal.objects.filter(id=journal_id).values()
    testing = Testing.objects.filter(id=testjournal[0]['testing_id']).values()
    test = Tests.objects.filter(id=testjournal[0]['test_id']).values()
    object_sf = ObjectSf.objects.filter(serial_num=test[0]['object_sf_num']).values()

    import os
    testInfo = parseTestFile(os.path.join(os.getcwd(), test[0]['file1']))

    # if testjournal[0]['status'] == 0:
    #     now = datetime.datetime.now(tz=timezone.utc)
    #     TestJournal.objects.filter(id=testjournal[0]['id']).update(begin_date=now, status=1)


    serialNum = test[0]['serial_num']

    # формирование ссылки на предыдущий тест
    sn = serialNum
    while True:
        sn-=1
        prevTest = Tests.objects.filter(serial_num=sn).values()
        if prevTest:
            if prevTest[0]['file1'] != None:
                prevTestID = prevTest[0]['id']
                break
        else:
            prevTestID = None
            break

    # формирование ссылки на следующий тест
    sn = serialNum
    while True:
        sn+=1
        nextTest = Tests.objects.filter(serial_num=sn).values()
        if nextTest:
            if nextTest[0]['file1'] != None:
                nextTestID = nextTest[0]['id']
                break
        else:
            nextTestID = None
            break


    result = {'os_name': testing[0]['os_name'] + ' ' + testing[0]['os_version'] + '.' + testing[0]['os_release'],
              'osf': object_sf[0]['name'],
              'name': test[0]['name'], 'status': testjournal[0]['status'], 'data': testInfo,
              'id': testjournal[0]['id'], 'comment': testjournal[0]['comment'], 'file2': test[0]['file2'],
              'prevTest': prevTestID, 'nextTest': nextTestID}

    return render(request, 'testeros/testing/test.html', {'result': result})


@login_required
def repomanager(request):
    settings = Settings.objects.all().values()
    return render(request, 'testeros/repomanager/start.html', {'stapelLst': json.loads(settings[0]['stapel']),
                                                               'repoLst': json.loads(settings[0]['repo'])})


@login_required
def repoinfo(request):
    settings = Settings.objects.all().values()
    return render(request, 'testeros/repomanager/info.html', {'repoLst': json.loads(settings[0]['repo'])})


@login_required
def repolog(request):
    actionlog_list = ActionLog.objects.order_by("-id")
    for i in actionlog_list:
        i.packages = json.loads(i.packages)

    paginator = Paginator(actionlog_list, 20)

    page = request.GET.get('page')
    try:
        actionlog = paginator.page(page)
    except PageNotAnInteger:
        actionlog = paginator.page(1)
    except EmptyPage:
        actionlog = paginator.page(paginator.num_pages)
    # print(actionlog.number)
    return render(request, 'testeros/repomanager/log.html', {"actionlog": actionlog})


@login_required
def buildiso(request):
    users = User.objects.all().values("id", "username")
    users_info = {}
    for user in users:
        users_info[user["id"]] = user["username"]


    logs = BuildIso_Log.objects.filter(status=1).values("id", "status", "user_id", "inform", "process_id", "created_at").order_by("-id")
    for n in logs:
        n["user_id"] = users_info[n["user_id"]]


    settings = BuildIsoSettings.objects.all().values('id', 'name', 'comment', 'created_at')
    return render(request, 'testeros/buildiso/start.html', {'log': logs, 'settings': settings})


@login_required
def buildisolog(request):
    users = User.objects.all().values("id", "username")
    users_info = {}
    for user in users:
        users_info[user["id"]] = user["username"]


    logs = BuildIso_Log.objects.all().values("id", "status", "user_id", "inform", "created_at", "close_at").order_by("-id")
    for n in logs:
        n["user_id"] = users_info[n["user_id"]]

    paginator = Paginator(logs, 20)

    page = request.GET.get('page')
    try:
        actionlog = paginator.page(page)
    except PageNotAnInteger:
        actionlog = paginator.page(1)
    except EmptyPage:
        actionlog = paginator.page(paginator.num_pages)

    return render(request, 'testeros/buildiso/log.html', {'log': actionlog})


@login_required
def settings(request):
    settings = Settings.objects.all().values()
    return render(request, 'testeros/settings/start.html', {'gl_iso': settings[0]['path_to_gl_iso'],
                                                            'ro_iso': settings[0]['path_to_ro_iso'],
                                                            'stapelLst': json.loads(settings[0]['stapel']),
                                                            'repoLst': json.loads(settings[0]['repo'])})