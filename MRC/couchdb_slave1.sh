#!/bin/bash
#step4

export ANSIBLE_HOST_KEY_CHECKING=False
. ./unimelb-comp90024-2021-grp-25-openrc.sh; ansible-playbook couchdb_slave1.yaml -i inventory/hosts.ini -u ubuntu --key-file=/Users/zhangziyang/Desktop/MRC/ProjectKey.pem