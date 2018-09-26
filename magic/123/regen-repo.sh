#!/bin/bash

##--SETTINGS--##
GOS_REPO="/mnt/hdd/gos_repo"
REDOS_REPO="/mnt/hdd/redos_repo"
##--END-SETTINGS--#

CONFIGURED="0"
CWD=`pwd`
#REPO_PATH=$2
ARCH="x86_64"
DEBUG_DIR="${ARCH}/debug"
SRPM_DIR="source/"
OS_DIR="${ARCH}/os"
COMPS=${CWD}"/mkiso/redos/comps.xml"

case $1 in
    goslinux)
	    COMPS="${CWD}/mkiso/goslinux/comps.xml"
	    REPO_PATH=${GOS_REPO}
	    CONFIGURED="1"
	    ;;
    redos)
	    COMPS="${CWD}/mkiso/redos/comps.xml"
	    REPO_PATH=${REDOS_REPO}
	    CONFIGURED="1"
	    ;;
    *)
	    echo "Must be goslinux or redos"
	    CONFIGURED="0"
	    ;;
esac

if [ $CONFIGURED -eq "1"  ]; then
    echo "Cleaning metadata ${REPO_PATH}..."
#    rm -fr ${REPO_PATH}/${DEBUG_DIR}/*repodata 
#    rm -fr ${REPO_PATH}/${SRPM_DIR}/*repodata
    rm -fr ${REPO_PATH}/${OS_DIR}/*repodata
    echo "Regenerating OS repo..."
    createrepo  -g ${COMPS} ${REPO_PATH}/${OS_DIR} 2>&1 > /dev/null
    echo "Regenerating SOURCE repo..."
    createrepo --update ${REPO_PATH}/${SRPM_DIR} 2>&1 > /dev/null
    echo "Regenerating DEBUG repo..."
    createrepo --update ${REPO_PATH}/${DEBUG_DIR} 2>&1 > /dev/null
    echo "Regeneration complete!"
fi