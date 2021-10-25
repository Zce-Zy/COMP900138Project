#!/bin/bash
export ANSIBLE_HOST_KEY_CHECKING=False
. ./unimelb-Comp900139-openrc.sh; ansible-playbook mrc.yaml

ansible-playbook install_environments.yaml -i inventory/hosts.ini -u ubuntu --key-file=/Users/zhangziyang/Desktop/MRC/ProjectKey.pem

