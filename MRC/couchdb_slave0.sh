#!/bin/bash
#step3

export ANSIBLE_HOST_KEY_CHECKING=False
. ./unimelb-Comp900139-openrc.sh; ansible-playbook couchdb_slave0.yaml -i inventory/hosts.ini -u ubuntu --key-file=/Users/zhangziyang/Desktop/MRC/ProjectKey.pem