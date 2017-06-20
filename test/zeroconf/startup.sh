#!/bin/bash
set -x
set -e

vagrant destroy -f
vagrant up one --provision
vagrant halt one

# delete the package.box if exists
[ -e package.box ] && rm -rf package.box

# package the box
vagrant package one

# add the box into vagrant
vagrant box add liquid-zeroconf ./package.box --force

# up the rest of the vms
vagrant up --provision
