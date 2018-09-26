#!/bin/bash
CUR_DIR=`pwd`
cd /tmp && pungi-koji --target-dir=/mnt/hdd/composes/redos --config $CUR_DIR/mkiso/redos7.conf --label=$1 --supported