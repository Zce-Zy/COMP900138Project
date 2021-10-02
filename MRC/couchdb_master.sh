#!/bin/bash
export ANSIBLE_HOST_KEY_CHECKING=False
. ./unimelb-Comp900139-openrc.sh; ansible-playbook couchdb_master.yaml -i inventory/hosts.ini -u ubuntu --key-file=/Users/zhangziyang/Desktop/MRC/ProjectKey.pem