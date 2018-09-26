#!/bin/bash
file_repo0='/etc/yum.repos.d/Koji-os72.repo'
touch $file_repo0
echo -n > $file_repo0
echo '[koji-os72]' >> $file_repo0
echo 'name=Koji-os72 - Stapel' >> $file_repo0
echo 'baseurl=http://stapel.red-soft.ru/kojifiles/repos/os72-build/latest/x86_64/' >> $file_repo0
echo 'enabled=1' >> $file_repo0
echo 'gpgcheck=0' >> $file_repo0
command="yum clean all"
eval $command
command="yum install -y fwbackups"
eval $command
rm $file_repo0
