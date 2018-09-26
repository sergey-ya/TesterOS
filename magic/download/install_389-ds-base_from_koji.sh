#!/bin/bash
file_repo0='/etc/yum.repos.d/Koji-dist-gl7.repo'
touch $file_repo0
echo -n > $file_repo0
echo '[koji-dist-gl7]' >> $file_repo0
echo 'name=Koji-dist-gl7 - Stapel' >> $file_repo0
echo 'baseurl=http://stapel.red-soft.ru/kojifiles/repos/dist-gl7-build/latest/x86_64/' >> $file_repo0
echo 'enabled=1' >> $file_repo0
echo 'gpgcheck=0' >> $file_repo0
command="yum clean all"
eval $command
command="yum install -y 389-ds-base"
eval $command
rm $file_repo0
