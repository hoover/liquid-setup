#!/bin/bash

###
# Build a Liquid image and save it to `shared/output`
###

set -e

SETUPDIR=/mnt/shared/setup
TARGET=/mnt/target
IMAGE=/mnt/shared/ubuntu-x86_64-raw.img

set -x

apt-add-repository -y ppa:ansible/ansible
apt-get update
apt-get install -y ansible git qemu-utils

curl https://liquidinvestigations.org/images/base_images/ubuntu-16.04-server-cloudimg-amd64-disk1.img > /mnt/shared/ubuntu-x86_64-cow2.img
qemu-img convert -f qcow2 -O raw /mnt/shared/ubuntu-x86_64-cow2.img $IMAGE

truncate -s 4G $IMAGE
# This assumes there is only one partition in the image.
# Keep start sector and type, but use all sectors up to the end of the image.
sfdisk -d $IMAGE | sed 's/size=[^,]\+,//' | sfdisk $IMAGE

losetup /dev/loop0 $IMAGE -o 1048576
resize2fs /dev/loop0
mkdir -p $TARGET
mount /dev/loop0 $TARGET
mount --bind /proc $TARGET/proc
mount --bind /dev $TARGET/dev
rm -f $TARGET/etc/resolv.conf
echo "nameserver 8.8.8.8" > $TARGET/etc/resolv.conf
touch $TARGET/etc/cloud/cloud-init.disabled

chroot $TARGET apt-get update
chroot $TARGET apt-get install -y python
chroot $TARGET apt-get clean

cd $SETUPDIR/ansible
touch vars/config.yml
ansible-playbook image_host_docker.yml

service docker stop
cp -a /var/lib/docker $TARGET/var/lib/docker

ansible-playbook image_chroot.yml

# console= setting referencing non-existant port can cause hangs during boot:
# https://bugs.launchpad.net/cloud-images/+bug/1573095
sed -i 's/console=hvc0 *//g' $TARGET/boot/grub/menu.lst
for i in $TARGET/boot/grub/grub.cfg $TARGET/etc/default/grub $TARGET/etc/default/grub.d/50-cloudimg-settings.cfg ; do
sed -i 's/ *console=ttyS0//g' $i
done

umount $TARGET/proc
umount $TARGET/dev
umount $TARGET
losetup -d /dev/loop0

echo "done; image saved in $IMAGE"
