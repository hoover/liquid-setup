#!/bin/bash

###
# Build a Liquid image and save it to `shared/output`
###

set -e

SETUPDIR=/mnt/shared/setup
TARGET=/mnt/target
IMAGE=/mnt/shared/ubuntu-odroid_c2-raw.img

set -x

apt-add-repository -y ppa:ansible/ansible
apt-get update
apt-get install -y ansible git pv

curl https://liquidinvestigations.org/images/base_images/ubuntu64-16.04-minimal-odroid-c2-20160815-4G.img.xz | xzcat > $IMAGE

losetup /dev/loop0 $IMAGE -o 135266304
mkdir -p $TARGET
mount /dev/loop0 $TARGET
mount --bind /proc $TARGET/proc
rm -f $TARGET/etc/resolv.conf
echo "nameserver 8.8.8.8" > $TARGET/etc/resolv.conf

chroot $TARGET apt-get update
chroot $TARGET apt-get install -y python
chroot $TARGET apt-get clean

cd $SETUPDIR/ansible
touch vars/config.yml
ansible-playbook image_host_docker.yml

service docker stop
cp -a /var/lib/docker $TARGET/var/lib/docker

ansible-playbook image_chroot.yml

umount $TARGET/proc
umount $TARGET
losetup -d /dev/loop0

echo "done; image saved in $IMAGE"
