#!/bin/bash

export PROJECT_ROOT=`pwd`
export BUILD_DIR=${PROJECT_ROOT}/build
export RELEASE_DIR=${PROJECT_ROOT}/release

function create_dir {
    FOLDER_NAME=$1
    if [ ! -d ${FOLDER_NAME} ]; then
        mkdir ${FOLDER_NAME}
    fi
}

# Find current branch
CURRENT=`git branch | grep '\*' | awk ' {print $2}'`

create_dir ${BUILD_DIR}
create_dir ${RELEASE_DIR}

# Export current branch to build directory

export APP_NAME=pysemcor
export APP_BUILD=${BUILD_DIR}/${APP_NAME}
export APP_RELEASE=${RELEASE_DIR}/${APP_NAME}

# clean old builds
rm -rf ${APP_BUILD}
rm -rf ${APP_RELEASE}

# release ISF
create_dir ${APP_BUILD}
git archive ${CURRENT} | tar -x -C ${APP_BUILD}
# release submodules
git submodule update
git submodule foreach --recursive 'git archive --verbose HEAD | tar -x -C ${APP_BUILD}/$path'

# Copy required files to release directory
create_dir ${APP_RELEASE}
# main packages
cp -rfv ${APP_BUILD}/pysemcor ${APP_RELEASE}/
cp -rfv ${APP_BUILD}/data ${APP_RELEASE}/
# setup.py, LICENSE, README, etc.
cp -rfv ${APP_BUILD}/setup.py ${APP_RELEASE}/
cp -rfv ${APP_BUILD}/LICENSE ${APP_RELEASE}/
cp -rfv ${APP_BUILD}/requirements.txt ${APP_RELEASE}/
cp -rfv ${APP_BUILD}/README.md ${APP_RELEASE}/
# submodules
cp -rfv ${APP_BUILD}/modules/chirptext/chirptext ${APP_RELEASE}/
cp -rfv ${APP_BUILD}/modules/puchikarui/puchikarui ${APP_RELEASE}/

cd ${RELEASE_DIR}
tar -zcvf ${APP_NAME}.tar.gz ${APP_NAME}
ls -l ${RELEASE_DIR}
