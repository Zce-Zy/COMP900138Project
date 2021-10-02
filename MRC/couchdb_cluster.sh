#!/bin/bash
#setp4
export ANSIBLE_HOST_KEY_CHECKING=False
. ./unimelb-Comp900139-openrc.sh; ansible-playbook couchdb_cluster_install.yaml -i inventory/hosts.ini -u ubuntu --key-file=/Users/zhangziyang/Desktop/MRC/ProjectKey.pem