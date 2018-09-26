-- test 1
UPDATE testeros_tests SET
prerequisites = 'Никаких предварительных операций производить не требуется.',
expected_result = 'Администратору   на   электронную   почту   поступает   уведомление   о   возможном нарушении информационной безопасности.',
test_procedure = 'От   имени   администратора   root   запускаем   редактор   конфигурационного   файла sudoers:
[code][root@goslinux etc]# visudo[/code]

Для начала редактирования нажать клавишу «insert», добавить записи следующего вида:
[code]Defaults mailto="root@localhost.localdomain"
Defaults mail_badpass
Defaults mail_no_perms
Defaults mail_no_user
Defaults mail_always[/code]

Этой   запись   настраивает   отправку   уведомлений   на   электронную   почту root@localhost.localdomain   администратора   root   уведомления   в   случае   обнаружения неуспешных попыток пользователя:
- выполнить команду sudo с неправильным паролем,
- если   вызывающему   пользователю   разрешено   использовать   sudo,   но   команда, которую он пытается выполнить, не указана в записи файла sudoers или явно запрещена,
- если вызывающий пользователь не находится в списке sudoers.

Для выхода из редактора, нажать клавишу Esc, ввести комбинацию  :wq для записи изменений и выхода из редактора.
От имени пользователя   ivanov попытаться выполнить команду sudo su с вводом неправильного пароля пользователя root:
[code][ivanov@goslinux ~]$ sudo su
[sudo] password for ivanov:
Sorry, try again.
[sudo] password for ivanov:
Sorry, try again.
[sudo] password for ivanov:
Sorry, try again.
sudo: 3 incorrect password attempts[/code]

От имени администратора root просмотреть содержимое почтового ящика:
[code][root@goslinux ivanov]# sudo mail -u root[/code]',
test_result = 'Администратору   на   электронную   почту   поступает   извещение   о   нарушении информационной безопасности вида:
[code]From root@goslinux.localdomain  Wed Oct 18 09:50:50 2017
Return-Path: <root@goslinux.localdomain>
X-Original-To: root@localhost.localdomain
Delivered-To: root@localhost.localdomain
To: root@localhost.localdomain
From: ivanov@goslinux.localdomain
Auto-Submitted: auto-generated
Subject: *** SECURITY information for goslinux ***
Date: Wed, 18 Oct 2017 09:50:50 +0300 (MSK)
Status: R
goslinux : Oct 18 09:50:50 : ivanov : user NOT in sudoers ; TTY=pts/1 ;
PWD=/home/ivanov ; USER=root ; COMMAND=/bin/su[/code]',
file1 = null, file2 = null WHERE serial_num = 1;

-- test 2
UPDATE testeros_tests SET
prerequisites = 'Никаких предварительных операций производить не требуется.',
expected_result = 'В журналах аудита, расположенных в папке /var/log должны появляться записи о всех заданных событиях безопасности.',
test_procedure = 'Произвести   действия,   нарушающие   установленные   политики   безопасности,   в
результате которых должно быть сформировано соответствующее событие безопасности.',
test_result = 'В журнала аудита появляются записи о событиях следующего вида (таблица 5.2):',
file1 = null, file2 = null WHERE serial_num = 2;

-- test 3
UPDATE testeros_tests SET
prerequisites = 'Никаких предварительных операций производить не требуется.',
expected_result = 'Только системный администратор имеет возможность чтения журналов аудита.',
test_procedure = 'С   помощью   утилиты   cat   от   имени   пользователя   ivanov   просмотреть   журналы аудита:   /var/log/audit/audit.log,   /var/log/secure   ,   /var/log/maillog   ,   /var/log/messages, /var/log/iptables/:
[code][ivanov@goslinux tmp]$ cat /var/log/audit/audit.log[/code]
С помощью утилиты cat от имени пользователя root просмотреть журналы аудита: /var/log/audit/audit.log, /var/log/secure , /var/log/maillog , /var/log/messages, /var/log/iptables/:
[code][root@goslinux tmp]# cat /var/log/audit/audit.log[/code]
От имени пользователей ivanov и root выполнить команду просмотра событий безопасности (например аутентификации пользователей):
[code][ivanov@goslinux ~]$ aureport -au[/code]
Пользователем ivanov запустить графическую утилиту просмотра журналов аудита из главного меню «Приложения» - «Системные» - «Программа просмотра журналов».',
test_result = 'При попытке просмотра журналов аудита пользователем ivanov возникает ошибка доступа:
[code]cat: /var/log/audit/audit.log: Отказано в доступе[/code]
Для администратора root журналы доступны для чтения. Информация выводится в заданном виде (таблица 5.2).
При попытке просмотра журналов аудита утилитой aureport от имени пользователя ivanov система сообщает об ошибке доступа и не позволяет чтение журналов:
[code]Authentication Report
============================================
# date time acct host term exe success event
============================================
Error opening config file (Отказано в доступе)
NOTE - using built-in logs: /var/log/audit/audit.log
Error opening /var/log/audit/audit.log (Отказано в доступе)
для   администратора   root   команда   выполняется   без   ошибок,   список   событий
отображается:
Authentication Report
============================================
# date time acct host term exe success event
============================================
Wrong number of arguments for line 1 in /etc/audit/auditd.conf
Not processing any more lines in /etc/audit/auditd.conf
NOTE - using built-in logs: /var/log/audit/audit.log
1. 19.09.2017 15:36:59 gdm ? ? /usr/libexec/gdm-session-worker yes 104
2. 19.09.2017 15:37:35 root ? ? /usr/libexec/gdm-session-worker yes 117
3. 19.09.2017 15:43:35 root ? pts/0 /usr/bin/su yes 157[/code]
При   попытке   просмотра   журналов   аудита   с   помощью   графической   утилиты «Программа просмотра журналов» пользователем ivanov программ запрашивает пароль администратора root и только после предъявления действительного пароля выводит главное окно программы, в котором можно просматривать журналы аудита.   Информация из журналов аудита, выводимая в программе просмотра, аналогична той, что представлена в таблице 3.2. При входе в программу без предъявления пароля (без привилегий) пользователь видит   несколько   системных   журналов,   не   содержащих   информацию   аудита информационной безопасности.',
file1 = null, file2 = null WHERE serial_num = 3;

-- test 4
UPDATE testeros_tests SET
prerequisites = 'Никаких предварительных операций производить не требуется.',
expected_result = 'Администратор имеет средства выборочного просмотра записей аудита.',
test_procedure = 'От   имени   администратора   root   выполнить   команду   просмотра   журнала   аудита
/var/log/secure:
[code][root@goslinux tmp]# cat /var/log/secure[/code]
просмотреть журнал аудита, только содержащие определенную дату - Sep 13:
[code][root@goslinux tmp]# cat /var/log/secure | grep ''Sep 13''[/code]
Просмотреть журнал аудита audit.log:
[code][root@goslinux tmp]# cat  /var/log/audit/audit.log[/code]
Найти в журнале аудита все записи содержащие одно из двух условий uid=1002 ИЛИ
type=USER_AUTH:
[code][root@goslinux   petrov]#  cat    /var/log/audit/audit.log  |  grep  -E  ''uid=1002|
type=USER_AUTH''[/code]
Найти в журнале аудита все записи обязательно содержащие два поля acct="petrov" И
res=failed:
[code][root@goslinux   petrov]#   cat      /var/log/audit/audit.log   |   grep   -E
''acct="petrov".*res=failed''[/code]
Отсортировать журнал аудита по 4 столбцу, содержащему UID пользователя:
[code][root@goslinux tmp]# sort -k4 /var/log/audit/audit.log[/code]
Использую   утилиту     ausearch   найти   все   события   безопасности,   связанные   с
идентификатором пользователя 1001:
[code][root@goslinux ivanov]# ausearch -ui 1001[/code]
Запустить утилиту из главного меню «Приложения» - «Системные» - «Программа
просмотра журналов». В меню «Фильтры» - «Управление фильтрами» нажать кнопку
«Добавить». В окне создания фильтра указать следующие данные:
- Имя: pid
- Регулярное выражение: pid=1
- Эффект: выбрать тип   «подсветка», сделать активным переключатель «текст»,
выбрать цвет подсветки красный.
Нажать кнопку «Применить».
Теперь   в   меню   «Фильтры»   сделать   активным   фильтр   «pid»   поставив   галочку
напротив соответствующего пункта меню.',
test_result = 'Администратор используя команды вывода и утилиты поиска заданных подстрок в
стандартном выводе может осуществлять поиск и сортировку данных журнала аудита.
При   использовании   графической   утилиты   просмотра   журналов   «Программа
просмотра   журналов»   с   помощью   настраиваемых   фильтров   администратор   может
осуществлять поиск заданных строк в журнале аудита по необходимым условиям.',
file1 = null, file2 = null WHERE serial_num = 4;

-- test5
UPDATE testeros_tests SET
prerequisites = 'Никаких предварительных операций производить не требуется.',
expected_result = 'Фиксируются только заданные фильтрами конфигурации аудита события.',
test_procedure = 'Для добавления и настройки правил используется команда auditctl.
Для настройки ведение аудита обращений к файлам из каталога /etc необходимо
ввести команду:
[code][root@goslinux petrov]# auditctl -w /etc/ -p wa -k access_etc[/code]
Также правила можно задавать редактируя файл etc/audit/audit.rules. В начале файла
размещаются несколько мета-правил, задающих конфигурацию и очищающих правила:
# Удаляем все правила из всех списков
-D
# Указываем количество буферов, хранящих сообщения аудита
-b 8192
#Что делать в чрезвычайной ситуации
-f 1
Далее необходимо добавить пользовательские правила безопасности:
# Наблюдение за конфигурационными файлами
-w /etc/audit/auditd.conf -p wa
-w /etc/audit/audit.rules -p wa
# Наблюдение за журнальными файлами
-w /var/log/audit/
-w /var/log/audit/audit.log
# Задания cron
-w /etc/cron.allow -p wa
-w /etc/cron.deny -p wa
-w /etc/cron.d/ -p wa
# Файлы паролей и групп
-w /etc/group -p wa
-w /etc/passwd -p wa
-w /etc/shadow
# Изменение прав доступа к файлам
-a entry,always -S chmod -S fchmod -S chown -S chown32 -S fchown -S fchown32
-S lchown -S lchown32
# Создание, открытие или изменение размеров файлов
-a entry,always -S creat -S open -S truncate -S truncate64 -S ftruncate -S
ftruncate64
# Создание и удаление каталогов
-a entry,always -S mkdir -S rmdir
# Удаление или создание ссылок
-a entry,always -S unlink -S rename -S link -S symlink
# Изменение расширенных атрибутов файлов
-a entry,always -S setxattr
-a entry,always -S lsetxattr
-a entry,always -S fsetxattr
-a entry,always -S removexattr
-a entry,always -S lremovexattr
-a entry,always -S fremovexattr
# Создание файлов устройств
-a entry,always -S mknod
# Монтирование файловых систем
-a entry,always -S mount -S umount -S umount2
# Использование системного вызова ptrace для отладки процессов
-a entry,always -S ptrace
# отслеживать системные вызовы unlink () и rmdir()
-a exit,always -S unlink -S rmdir
# отслеживать системные вызовы open () от пользователя с UID 1001
-a exit,always -S open -F loginuid=1001
Изменения конфигурации вступят в силу после перезапуска демона auditd:
[code][root@goslinux petrov]# service auditd restart[/code]',
test_result = 'Фиксируются только заданные фильтрами конфигурации аудита события. ',
file1 = null, file2 = null WHERE serial_num = 5;

-- test6
UPDATE testeros_tests SET
prerequisites = 'Никаких предварительных операций производить не требуется.',
expected_result = 'Журналы   аудита   недоступны   для   изменения/удаления   непривилегированному
пользователю. Для системного администратор root доступны все операции с журналами
аудита.',
test_procedure = 'Пользователем ivanov попытаться удалить
журналы аудита /var/log/audit/audit.log,
/var/log/secure , /var/log/maillog , /var/log/messages, /var/log/iptables/:
[code][ivanov@goslinux ~]$ rm /var/log/messages[/code]
Администратором root попытаться удалить журналы аудита /var/log/audit/audit.log,
/var/log/secure , /var/log/maillog , /var/log/messages, /var/log/iptables/:
[code][root@goslinux ivanov]# rm /var/log/messages
rm: удалить обычный файл «/var/log/messages»? y[/code]
Пользователем   ivanov   попытаться   внести   изменения   в   журналы   аудита
/var/log/audit/audit.log, /var/log/secure , /var/log/maillog , /var/log/messages, /var/log/iptables/:
[code][ivanov@goslinux ~]$ nano /var/log/secure[/code]
Администратором   root   попытаться   внести   изменения   в   журналы   аудита
/var/log/audit/audit.log, /var/log/secure , /var/log/maillog , /var/log/messages, /var/log/iptables/:
[code][root@goslinux ivanov]# nano /var/log/secure[/code]',
test_result = 'Журналы   аудита   недоступны   для   изменения/удаления   непривилегированному
пользователю. При попытке удалить файл пользователь ivanov получает сообщение об
ошибке вида:
rm: удалить защищенный от записи обычный файл «/var/log/messages»? y
rm: невозможно удалить «/var/log/messages»: Отказано в доступе
При попытке редактирования файла аудита с помощью редактора nano выводится
ошибка вида:
[ Ошибка чтения /var/log/secure: Отказано в доступе ]
Для администратора root все журналы аудита доступны как для редактирования так и
для удаления. ',
file1 = null, file2 = null WHERE serial_num = 6;

--  test7
UPDATE testeros_tests SET
prerequisites = 'Никаких предварительных операций производить не требуется.',
expected_result = 'Сигналом   тревоги,   генерируемым   ОО,   может   являться   сообщение   системного
журнала или уведомление пользователя по электронной почте. Это сообщение генерируется,
когда потребности журнала аудита превышают предел, определенный в файле auditd.conf.',
test_procedure = 'От   имени   администратора   root   изменить
следующие   параметры   в
  файле
конфигурации службы аудита
/etc/audit/auditd.conf :
- минимум свободного пространства в мегабайтах, по достижении которого должно
быть осуществлено оповещение:
[code]space_left = 100[/code]
- действие предпринимаемое при достижении объёмом свободного пространства на
диске указанного минимума. Допустимые значения - ignore, syslog, email, exec, suspend,
single и halt. При значении syslog в системный протокол добавляется соответствующая
запись.   При   значении   email   по   адресу   указанному   в   action_mail_acct   отправляется
уведомление.
[code]space_left_action =  syslog[/code]
или
[code]space_left_action = EMAIL
action_mail_acct = root@localhost.localdomain[/code]
В   параметре   space_left   задать   значение   заведомо   превышающее     имеющееся
свободное пространство или произвести действия по переполнению файловой системы,
хранящей данные аудита.
Перезагрузить ЭВМ. ',
test_result = 'При превышении заданного порога минимально необходимого пространства для
записи журналов аудита формируется сигнал тревоги. В журнал аудита записывается
уведомление вида:
[code]Nov  2 14:40:22 goslinux auditd[741]: Audit daemon is low on disk space for
logging[/code]
Или   на   электронную   почту   администратора   отправляется   письмо   следующего
содержания:
[code][root@goslinux ivanov]# sudo mail -u root
Heirloom Mail version 12.5 7/5/10.  Type ? for help.
"/var/mail/root": 1 message 1 new
>N   1 root@goslinux.locald   Mon Nov 20 15:57   15/598     "Audit Disk Space
Alert"
& 1
Message  1:
From root@localhost.localdomain  Mon Nov 20 15:57:36 2017
Return-Path: <root@localhost.localdomain>
X-Original-To: root@localhost.localdomain
Delivered-To: root@localhost.localdomain
To: root@localhost.localdomain
From: root@goslinux.localdomain
Subject: Audit Disk Space Alert
Date: Thu,  2 Nov 2017 14:44:52 +0300 (MSK)
Status: R
The audit daemon is low on disk space for logging! Please take action
to ensure no loss of service.[/code]',
file1 = null, file2 = null WHERE serial_num = 7;

-- test8
UPDATE testeros_tests SET
prerequisites = 'Никаких предварительных операций производить не требуется.',
expected_result = 'При   помощи   файла   конфигурации   аудита
/etc/auditd.conf   администратор   может
определять поведение ОС в случае обнаружения отсутствия свободного пространства на
диске, отведенном для размещения журналов аудита.',
test_procedure = 'От   имени   администратора   root   изменить
следующие   параметры   в
  файле
конфигурации службы аудита
/etc/audit/auditd.conf :
- действие предпринимаемое при обнаружении отсутствия свободного пространства
на диске. Указание single приведёт к переводу компьютера в однопользовательский режим:
[code]disk_full_action =  SINGLE[/code]
- действие предпринимаемое при возникновении ошибки в работе с диском:
[code]disk_error_action =  SINGLE[/code]
- минимум свободного пространства в мегабайтах, по достижении которого должно
быть осуществлено оповещение:
[code]space_left = 100[/code]
- критический минимум свободного пространства в мегабайтах, при достижении
которого должно выполняться действие определяемое параметром admin_space_left_action:
[code]admin_space_left = 99[/code]
- действие предпринимаемое при достижении объёмом свободного пространства на
диске указанного критического минимума:
[code]admin_space_left_action = SINGLE[/code]
Значение   параметра   space_left   должно   быть   больше   значения   параметра
[code]admin_space_left.[/code]
Далее производятся действия на переполнение файловой системы, хранящей данные
аудита или имитируются сбои в работе жесткого диска.
Перезагрузить ЭВМ.',
test_result = 'При   невозможности   сохранения   данных   аудита   система   переходит   в
однопользовательский   режим.   Только   администратору   root   доступна   работа   с   ОС.
Предполагается, что администратор освободит место и после появления на жестком диске
необходимого свободного пространства работа ОС будет восстановлена. ',
file1 = null, file2 = null WHERE serial_num = 8;

--  test9
UPDATE testeros_tests SET
prerequisites = 'От имени администратора root в каталоге tmp создать 4 подкаталога:
[code][root@goslinux ivanov]# mkdir /tmp/dir_wr
[root@goslinux ivanov]# mkdir /tmp/dir_read
[root@goslinux ivanov]# mkdir /tmp/dir_exec
[root@goslinux ivanov]# mkdir /tmp/dir_wr_read[/code]
Для созданного каталога dir_wr установить права только на изменение каталога для
владельца и группы владельца каталога:
[code][root@goslinux ivanov]# chmod 330 /tmp/dir_wr/[/code]
Для созданного каталога dir_read установить права только на чтение имён файлов для
владельца и группы владельца каталога:
[code][root@goslinux ivanov]# chmod 440 /tmp/dir_read/[/code]
Для созданного каталога dir_wr_read установить права на чтение и запись для
владельца и группы владельца каталога:
[code][root@goslinux ivanov]# chmod 660 /tmp/dir_wr_read/[/code]
Для   созданного   каталога   dir_exec   установить   права   на   получение   доступа   к
метаданным о файлах для владельца и группы владельца каталога:
[code][root@goslinux ivanov]# chmod 110 /tmp/dir_exec/[/code]
Просмотреть права созданных каталогов:
[code][root@goslinux ivanov]# ls -l /tmp/
итого 40
d--x--x---. 2 root   root   4096 сен 18 09:55 dir_exec
dr--r-----. 2 root   root   4096 сен 18 09:55 dir_read
d-wх-wх---. 2 root   root   4096 сен 18 09:55 dir_wr
drw-rw----. 2 root   root   4096 сен 18 09:59 dir_wr_read[/code]
Создать тестовый каталог  tst_fldr и в нем 4 файла:
[code][root@goslinux audit]# mkdir /tmp/tst_fldr/
[root@goslinux audit]# touch /tmp/tst_fldr/read_only.txt
[root@goslinux audit]# touch /tmp/tst_fldr/write_only.txt
[root@goslinux audit]# touch /tmp/tst_fldr/exec_only.sh
[root@goslinux audit]# touch /tmp/tst_fldr/rw.txt[/code]
Для созданного файла read_only.txt установить права только на чтение для владельца
и группы владельца каталога:
[code][root@goslinux audit]# chmod 440 /tmp/tst_fldr/read_only.txt[/code]
Для созданного файла write_only.txt установить права только на запись для владельца
и группы владельца каталога:
[code][root@goslinux audit]# chmod 220 /tmp/tst_fldr/write_only.txt[/code]
Для созданного файла rw.txt установить права на запись и чтение для владельца и
группы владельца каталога:
[code][root@goslinux audit]# chmod 660 /tmp/tst_fldr/rw.txt[/code]
Для   созданного   файла   exec_only.sh   установить   права   только   на   выполнение
(пользователь также должен иметь разрешение на чтение) для владельца   и группы
владельца каталога:
[code][root@goslinux audit]# chmod 550 /tmp/tst_fldr/exec_only.sh[/code]
Просмотреть права созданных файлов:
[code][root@goslinux tmp]# ls -l /tmp/tst_fldr/
итого 0
-r-xr-x---. 1 root root 0 сен 15 15:46 exec_only.sh
-r--r-----. 1 root root 0 сен 15 15:32 read_only.txt
-rw-rw----. 1 root root 0 сен 15 15:33 rw.txt
--w--w----. 1 root root 0 сен 15 15:33 write_only.txt[/code]
Владельцем всех созданных файлов и каталогов является пользователь root.',
expected_result = 'ФБ ОС осуществляет дискреционную политику доступа для объектов файловой
системы.',
test_procedure = 'а) Пользователями ivanov и petrov просмотреть содержимое файлов в каталоге tst_fldr:
[code][petrov@goslinux tmp]$ cat /tmp/tst_fldr/read_only.txt
[petrov@goslinux tmp]$ cat /tmp/tst_fldr/rw.txt
[petrov@goslinux tmp]$ cat /tmp/tst_fldr/write_only.txt
[petrov@goslinux tmp]$ cat /tmp/tst_fldr/exec_only.sh[/code]
пользователями ivanov и petrov записать текст в файлы каталога  tst_fldr:
[code][petrov@goslinux tmp]$ echo "txt" > /tmp/tst_fldr/read_only.txt
[petrov@goslinux tmp]$ echo "txt" > /tmp/tst_fldr/rw.txt
[petrov@goslinux tmp]$ echo "txt" > /tmp/tst_fldr/write_only.txt
[petrov@goslinux tmp]$ echo "txt" > /tmp/tst_fldr/exec_only.sh[/code]
пользователями ivanov и petrov выполнить файлы каталога  tst_fldr:
[code][petrov@goslinux tmp]$ /tmp/tst_fldr/exec_only.sh
[petrov@goslinux tmp]$ /tmp/tst_fldr/rw.txt
[petrov@goslinux tmp]$ /tmp/tst_fldr/write_only.txt
[petrov@goslinux tmp]$ /tmp/tst_fldr/read_only.txt[/code]
б) Пользователем root назначить владельцем каталога tst_fldr и всех файлов в нем
пользователя ivanov:
[code][root@goslinux ivanov]# chown -R ivanov /tmp/tst_fldr/[/code]
Проверить правильность назначенных прав:
[code][root@goslinux ivanov]# ls -l /tmp/tst_fldr/
итого 8
-r-xr-x---. 1 ivanov root 0 сен 15 15:46 exec_only.sh
-r--r-----. 1 ivanov root 0 сен 15 15:32 read_only.txt
-rw-rw----. 1 ivanov root 4 сен 18 10:42 rw.txt
--w--w----. 1 ivanov root 4 сен 18 10:41 write_only.txt[/code]
Владельцем всех созданных файлов является пользователь ivanov.
Пользователями ivanov и petrov повторить попытки чтения, записи, запуска файлов в
каталоге tst_fldr.
в) Пользователем root назначить владельцем каталога tst_fldr и всех файлов в нем
пользователя root, группой владельца назначить ivanov:
[code][root@goslinux ivanov]# chown -R root:ivanov /tmp/tst_fldr/[/code]
Проверить правильность назначенных прав:
[code][root@goslinux ivanov]# ls -l /tmp/tst_fldr/
итого 8
-r-xr-x---. 1 root ivanov 0 сен 15 15:46 exec_only.sh
-r--r-----. 1 root ivanov 0 сен 15 15:32 read_only.txt
-rw-rw----. 1 root ivanov 4 сен 18 10:42 rw.txt
--w--w----. 1 root ivanov 4 сен 18 10:41 write_only.txt[/code]
Владельцем всех созданных файлов является пользователь root, группа ivanov.
Пользователями ivanov и petrov повторить попытки чтения, записи, запуска файлов в
каталоге tst_fldr.
г) Добавить пользователей ivanov и petrov в группу audio:
[code][root@goslinux ivanov]# usermod -a -G audio ivanov
[root@goslinux ivanov]# usermod -a -G audio petrov[/code]
Пользователем root назначить владельцем каталога tst_fldr и всех файлов в нем
пользователя root, группой владельца назначить audio:
[code][root@goslinux ivanov]# chown -R root:audio /tmp/tst_fldr/[/code]
Проверить правильность назначенных прав:
[code][root@goslinux ivanov]# ls -l /tmp/tst_fldr/
итого 8
-r-xr-x---. 1 root audio 0 сен 15 15:46 exec_only.sh
-r--r-----. 1 root audio 0 сен 15 15:32 read_only.txt
-rw-rw----. 1 root audio 4 сен 18 11:21 rw.txt
--w--w----. 1 root audio 4 сен 18 11:21 write_only.txt[/code]
Владельцем всех созданных файлов является пользователь root, группа audio.
Для применения назначенных групп завершить текущие сеансы пользователей ivanov
и petrov.
Начать новые сеансы от имени  пользователей ivanov и petrov. Убедиться, что новая
группа доступна пользователю:
[code][petrov@goslinux ivanov]$ id
uid=1001(petrov)         gid=1001(petrov)         группы=1001(petrov),63(audio)
контекст=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023[/code]
Пользователями ivanov и petrov повторить попытки чтения, записи, запуска файлов в
каталоге tst_fldr.
д) Владельцем созданных каталогов  dir_exec,  dir_read. dir_wr,  dir_wr_read является
пользователь root группа владельца root. Пользователи ivanov и petrov не входят в группу
root.
Пользователями ivanov и petrov просмотреть содержимое каталогов:
[code][ivanov@goslinux tmp]$ ls -l /tmp/dir_exec/
[ivanov@goslinux tmp]$ ls -l /tmp/dir_read/
[ivanov@goslinux tmp]$ ls -l /tmp/dir_wr/
[ivanov@goslinux tmp]$ ls -l /tmp/dir_wr_read/[/code]
Пользователями ivanov и petrov в каждом каталоге создать файл test.txt:
[code][ivanov@goslinux tmp]$ touch /tmp/dir_exec/test.txt
[ivanov@goslinux tmp]$ touch /tmp/dir_read/test.txt
[ivanov@goslinux tmp]$ touch /tmp/dir_wr/test.txt
[ivanov@goslinux tmp]$ touch /tmp/dir_wr_read/test.txt[/code]
Пользователями ivanov и petrov сменить текущий каталог:
[code][ivanov@goslinux tmp]$ cd /tmp/dir_exec/
[ivanov@goslinux tmp]$ cd /tmp/dir_read/
[ivanov@goslinux tmp]$ cd /tmp/dir_wr/
[ivanov@goslinux tmp]$ cd /tmp/dir_wr_read/[/code]
e) Сменить владельца каталогов   dir_exec,   dir_read. dir_wr,   dir_wr_read назначив
новым владельцем пользователя ivanov:
[code][root@goslinux ivanov]# chown ivanov /tmp/dir_exec/
[root@goslinux ivanov]# chown ivanov /tmp/dir_read/
[root@goslinux ivanov]# chown ivanov /tmp/dir_wr/
[root@goslinux ivanov]# chown ivanov /tmp/dir_wr_read/[/code]
Проверить правильность назначенных прав:
[code][root@goslinux ivanov]# ls -l /tmp/
итого 48
d--x--x---. 2 ivanov root   4096 сен 18 09:55 dir_exec
dr--r-----. 2 ivanov root   4096 сен 18 09:55 dir_read
d-wх-wх---. 2 ivanov root   4096 сен 18 09:55 dir_wr
drw-rw----. 2 ivanov root   4096 сен 18 09:59 dir_wr_read[/code]
Пользователями   ivanov   и   petrov   просмотреть   содержимое   каталогов,   в   каждом
каталоге создать файл test.txt,  сменить текущий каталог.
ж) Сменить владельца каталогов  dir_exec,  dir_read. dir_wr,  dir_wr_read назначив
новым владельцем пользователя root и назначив группу владельца ivanov:
[code][root@goslinux ivanov]# chown root:ivanov /tmp/dir_exec/
[root@goslinux ivanov]# chown root:ivanov /tmp/dir_read/
[root@goslinux ivanov]# chown root:ivanov /tmp/dir_wr/
[root@goslinux ivanov]# chown root:ivanov /tmp/dir_wr_read/[/code]
Проверить правильность назначенных прав:
[code][root@goslinux ivanov]# ls -l /tmp/
итого 48
d--x--x---. 2 root   ivanov 4096 сен 18 09:55 dir_exec
dr--r-----. 2 root   ivanov 4096 сен 18 09:55 dir_read
d-wx-wx---. 2 root   ivanov 4096 сен 18 12:26 dir_wr
drw-rw----. 2 root   ivanov 4096 сен 18 09:59 dir_wr_read[/code]
з) Сменить владельца каталогов   dir_exec,   dir_read. dir_wr,   dir_wr_read назначив
новым владельцем пользователя root и назначив группу владельца audio:
[code][root@goslinux ivanov]# chown root:audio /tmp/dir_wr_read/
[root@goslinux ivanov]# chown root:audio /tmp/dir_wr/
[root@goslinux ivanov]# chown root:audio /tmp/dir_read/
[root@goslinux ivanov]# chown root:audio /tmp/dir_exec/[/code]
Проверить правильность назначенных прав:
[code][root@goslinux ivanov]# ls -l /tmp/
итого 48
d--x--x---. 2 root   audio  4096 сен 18 09:55 dir_exec
dr--r-----. 2 root   audio  4096 сен 18 09:55 dir_read
d-wx-wx---. 2 root   audio  4096 сен 18 12:26 dir_wr
drw-rw----. 2 root   audio  4096 сен 18 09:59 dir_wr_read[/code]
и) Пользователем ivanov создать файл:
[code][ivanov@goslinux dir_wr]$ touch /tmp/ivanov.file[/code]
Назначить ему права с полным доступом для всех пользователей и дополнительным
атрибутом Sticky bit:
[code][ivanov@goslinux dir_wr]$ chmod 1777 /tmp/ivanov.file[/code]
Пользователем   root   сменить   группу   владельца   файла   на   общедоступную   для
пользователей ivanov и petrov:
[code][root@goslinux ivanov]# chown ivanov:audio /tmp/ivanov.file[/code]
Проверить правильность назначенных прав:
[code][ivanov@goslinux dir_wr]$ ls -l /tmp
итого 48
-rwxrwxrwt. 1 ivanov audio     0 сен 18 15:06 ivanov.file[/code]
Пользователем  petrov удалить  файл ivanov.file:
[code][petrov@goslinux dir_wr]$ rm /tmp/ivanov.file[/code]
Пользователем ivanov удалить  файл ivanov.file:
[code][ivanov@goslinux dir_wr]$ rm /tmp/ivanov.file[/code]',
test_result = 'ФБ ОС осуществляет дискреционную политику доступа для объектов файловой
системы.
а) Так как доступ к файлам в каталоге tst_fldr предоставлен только пользователю root
и группе root, то при попытке выполнения операций с файлами другими пользователями
(ivanov, petrov) возникают ошибки доступа. При попытке чтения:
[code]cat: /tmp/tst_fldr/exec_only.sh: Отказано в доступе[/code]
при попытке записи:
[code]bash: /tmp/tst_fldr/read_only.txt: Отказано в доступе[/code]
при попытке запуска:
[code]bash: /tmp/tst_fldr/exec_only.sh: Отказано в доступе[/code]
Ни одна из операций успешно не заканчивается.
б) После назначения владельцем файлов пользователя ivanov при попытке чтения
файлов пользователем ivanov успешно завершаются операции чтения файлов read_only.txt,
rw.txt и exec_only.sh. При попытке чтения файла  write_only.txt возникает ошибка доступа:
[code]cat: /tmp/tst_fldr/write_only.txt: Отказано в доступе[/code]
Для пользователя petrov недоступны для чтения все файлы. Все попытки чтения
заканчиваются ошибкой доступа.
При попытке записи пользователем ivanov успешно удается записать данные в файлы
write_only.txt и rw.txt. Остальные файлы недоступны для записи. Возникает ошибка доступа:
[code]bash: /tmp/tst_fldr/read_only.txt: Отказано в доступе[/code]
Для пользователя petrov недоступны для записи все файлы. Все попытки записи
заканчиваются ошибкой доступа.
При попытке исполнения файлов пользователем ivanov успешно удается выполнить
только файл exec_only.sh. Остальные файлы недоступны для выполнения. Возникает ошибка
доступа:
[code]bash: /tmp/tst_fldr/rw.txt: Отказано в доступе[/code]
Для пользователя petrov недоступны для выполнения все файлы. Все попытки
выполнить файл заканчиваются ошибкой доступа.
в) После назначения владельцем файлов пользователя root и группой пользователя
ivanov при попытке чтения файлов пользователем ivanov, который входит в группу ivanov,
успешно завершаются операции чтения файлов read_only.txt, rw.txt и exec_only.sh. При
попытке чтения файла  write_only.txt возникает ошибка доступа:
[code]cat: /tmp/tst_fldr/write_only.txt: Отказано в доступе[/code]
Для пользователя petrov, который не входит в группу ivanov, недоступны для чтения
все файлы. Все попытки чтения заканчиваются ошибкой доступа.
При попытке записи пользователем ivanov успешно удается записать данные в файлы
write_only.txt и rw.txt. Остальные файлы недоступны для записи. Возникает ошибка доступа:
[code]bash: /tmp/tst_fldr/read_only.txt: Отказано в доступе[/code]
Для пользователя petrov недоступны для записи все файлы. Все попытки записи
заканчиваются ошибкой доступа.
При попытке исполнения файлов пользователем ivanov успешно удается выполнить
только файл exec_only.sh. Остальные файлы недоступны для выполнения. Возникает ошибка
доступа:
[code]bash: /tmp/tst_fldr/rw.txt: Отказано в доступе[/code]
Для пользователя petrov недоступны для выполнения все файлы. Все попытки
выполнить файл заканчиваются ошибкой доступа.
г) После назначения владельцем файлов пользователя root и группой пользователя
audio при попытке чтения файлов пользователями ivanov и petrov, которые входят в группу
audio, успешно завершаются операции чтения файлов read_only.txt, rw.txt и exec_only.sh.
При попытке чтения файла  write_only.txt возникает ошибка доступа:
[code]cat: /tmp/tst_fldr/write_only.txt: Отказано в доступе[/code]
При попытке записи пользователями ivanov и petrov успешно удается записать
данные в файлы write_only.txt и rw.txt. Остальные файлы недоступны для записи. Возникает
ошибка доступа:
[code]bash: /tmp/tst_fldr/read_only.txt: Отказано в доступе[/code]
При попытке исполнения файлов пользователями ivanov и petrov успешно удается
выполнить  только   файл   exec_only.sh.  Остальные   файлы   недоступны   для   выполнения.
Возникает ошибка доступа:
[code]bash: /tmp/tst_fldr/rw.txt: Отказано в доступе[/code]
д) Так как доступ к каталогам предоставлен только пользователю root и группе root,
то при попытке выполнения операций с каталогами другими пользователями (ivanov, petrov)
возникают ошибки доступа. При попытке чтения:
[code]ls: невозможно открыть каталог /tmp/dir_exec/: Отказано в доступе[/code]
При попытке записи:
[code]touch:   невозможно   выполнить   touch   для   «/tmp/dir_exec/test.txt»:   Отказано   в
доступе[/code]
При попытке выполнения:
[code]bash: cd: /tmp/dir_exec/: Отказано в доступе[/code]
е) После назначения новым владельцем каталогов пользователя ivanov операции
просмотра   содержимого   каталогов     dir_read   и     dir_wr_read   пользователем   ivanov
завершаются   успешно.   Для   остальных   каталогов   просмотр   запрещен,   пользователю
выводится уведомление об ошибке доступа:
[code]ls: невозможно открыть каталог /tmp/dir_exec/: Отказано в доступе[/code]
Попытки создания файла внутри каталога пользователем ivanov   заканчиваются
успешно только для каталога   dir_wr. Во всех остальных каталогах создание файлов
запрещено. Пользователю выводится предупреждение:
[code]touch:   невозможно   выполнить   touch   для   «/tmp/dir_exec/test.txt»:   Отказано   в
доступе[/code]
Попытки сменить текущий каталог пользователем ivanov успешно завершаются
только для каталогов   dir_exec и   dir_wr. Смена каталога для остальных запрещена.
Пользователь получает сообщение об ошибке:
[code]bash: cd: /tmp/dir_read/: Отказано в доступе[/code]
Для пользователь petrov все операции заканчиваются ошибкой.
ж) После назначения новым владельцем каталогов пользователя root и группой
владельца ivanov операции просмотра содержимого каталогов   dir_read и   dir_wr_read
пользователем ivanov завершаются успешно. Для остальных каталогов просмотр запрещен,
пользователю выводится уведомление об ошибке доступа:
[code]ls: невозможно открыть каталог /tmp/dir_exec/: Отказано в доступе[/code]
Попытки создания файла внутри каталога пользователем ivanov   заканчиваются
успешно только для каталога   dir_wr. Во всех остальных каталогах создание файлов
запрещено. Пользователю выводится предупреждение:
[code]touch:   невозможно   выполнить   touch   для   «/tmp/dir_exec/test.txt»:   Отказано   в
доступе[/code]
Попытки сменить текущий каталог пользователем ivanov успешно завершаются
только для каталогов   dir_exec и   dir_wr. Смена каталога для остальных запрещена.
Пользователь получает сообщение об ошибке:
[code]bash: cd: /tmp/dir_read/: Отказано в доступе[/code]
Для пользователь petrov все операции заканчиваются ошибкой.
з) После назначения новым владельцем каталогов пользователя root и группой
владельца audio (в которую входят пользователи ivanov и petrov) операции просмотра
содержимого каталогов  dir_read и  dir_wr_read пользователями ivanov и petrov завершаются
успешно.   Для   остальных   каталогов   просмотр   запрещен,   пользователям   выводится
уведомление об ошибке доступа:
[code]ls: невозможно открыть каталог /tmp/dir_exec/: Отказано в доступе[/code]
Попытки   создания   файла   внутри   каталога   пользователями   ivanov   и   petrov
заканчиваются успешно только для каталога  dir_wr. Во всех остальных каталогах создание
файлов запрещено. Пользователю выводится предупреждение:
[code]touch:   невозможно   выполнить   touch   для   «/tmp/dir_exec/test.txt»:   Отказано   в
доступе[/code]
Попытки   сменить   текущий   каталог   пользователями   ivanov   и   petrov   успешно
завершаются только для каталогов   dir_exec и   dir_wr. Смена каталога для остальных
запрещена. Пользователь получает сообщение об ошибке:
[code]bash: cd: /tmp/dir_read/: Отказано в доступе[/code]
и) Специальный атрибут sticky bit используется в основном для каталогов, чтобы
защитить в них файлы. Из такого каталога пользователь может удалить только те файлы,
владельцем которых он является.
Несмотря на то, что на файл  ivanov.file выставлены неограниченные права, которые
позволяют проводить любые операции с файлом всем пользователям и то, что пользователь
petrov состоит в группе audio владельца файла, попытка удаления файла будет неуспешной:
[code]rm: невозможно удалить «/tmp/ivanov.file»: Операция не позволена[/code]
А владелец файла пользователь ivanov сможет удалить файл.',
file1 = null, file2 = null WHERE serial_num = 9;


--  maket
-- UPDATE testeros_tests SET
-- prerequisites = '',
-- expected_result = '',
-- test_procedure = '',
-- test_result = '',
-- file1 = null, file2 = null WHERE serial_num = 2;
