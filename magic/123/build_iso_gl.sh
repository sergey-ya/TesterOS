#!/bin/bash
CUR_DIR=`pwd`
cd /tmp && pungi-koji --target-dir=/mnt/hdd/composes/fssp --config $CUR_DIR/mkiso/gl7.conf.02102017 --label=$1 --supported