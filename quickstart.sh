#!/bin/bash

TEMPDIR=$(mktemp -d)

cleanup() {
  rm -rf "${TEMPDIR}"
}

python3 -m venv "${TEMPDIR}/osp_probe"

${TEMPDIR}/osp_probe/bin/pip3 install -U pip
${TEMPDIR}/osp_probe/bin/pip3 install -U setuptools
${TEMPDIR}/osp_probe/bin/pip3 install python-openstackclient

export OS_CLIENT_CONFIG_FILE=${PWD}/clouds.yaml
${TEMPDIR}/osp_probe/bin/python3 ${PWD}/probe_osp.py 

cleanup
