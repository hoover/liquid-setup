#!/bin/bash

###
# Take raw Liquid image and convert it to other formats
###

set -e

SETUPDIR=/mnt/shared/setup
TARGET=/mnt/target
TEMPDIR=/tmp
OUTPUT=/mnt/shared/output
IMAGE=/mnt/shared/ubuntu-x86_64-raw.img
TEMPIMG=/mnt/shared/temp-image.img

# TODO: Remove defaulting to virtualbox when buildbot supports arguments
if [ -n "$1" ]; then
    FORMAT="$1"
else
    FORMAT=virtualbox
fi

if [ "x$FORMAT" = xvirtualbox ]; then
    DEST="$OUTPUT/ubuntu-x86_64-vbox.box"
    VMNAME=liquid
    HOSTINST="virtualbox vagrant"
else
    echo Usage: $0 image_type [source] [dest]
    echo
    echo Types: virtualbox
    exit 1
fi

if [ -n "$2" ]; then
    IMAGE="$2"
fi

if [ -n "$3" ]; then
    DEST="$3"
fi

if [ -a "$DEST" ]; then
    # vagrant package fails if output file exists
    echo "Output file $DEST already exists. Exiting."
    exit 1
fi

set -x

# Install tools needed for image conversion
if [ -n "$HOSTINST" ]; then
    apt-get update
    apt-get install -y --no-install-recommends $HOSTINST
fi

# Create copy of image so source image is not altered
# (eg. You wouldn't want VMWare tools on a VirtualBox image)
cp "$IMAGE" "$TEMPIMG"

# Mount temp image and set up for chroot
losetup /dev/loop0 "$TEMPIMG" -o 1048576
mkdir -p $TARGET
mount /dev/loop0 $TARGET
mount --bind /proc $TARGET/proc
mount --bind /dev $TARGET/dev

###
# Set up things Vagrant needs on any image

# Create ssh host keys
ssh-keygen -f $TARGET/etc/ssh/ssh_host_rsa_key -N '' -t rsa
ssh-keygen -f $TARGET/etc/ssh/ssh_host_dsa_key -N '' -t dsa

# Fix DNS to use google (resolves problems accessing archive.debian.com &c.)
mv $TARGET/etc/resolv.conf $TARGET/etc/resolv.conf.orig
echo "nameserver 8.8.8.8" > $TARGET/etc/resolv.conf

# Create vagrant user for ssh
chroot $TARGET adduser vagrant --gecos "Vagrant User,,," --disabled-password
mkdir -p $TARGET/home/vagrant/.ssh
# Insecure key! Vagrant will replace it with randomly generated key.
echo ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA6NF8iallvQVp22WDkTkyrtvp9eWW6A8YVr+kz4TjGYe7gHzIw+niNltGEFHzD8+v1I2YJ6oXevct1YeS0o9HZyN1Q9qgCgzUFtdOKLv6IedplqoPkcmF0aYet2PkEDo3MlTBckFXPITAMzF8dJSIFo9D8HfdOV0IAdx4O7PtixWKn5y2hMNG0zQPyUecp4pzC6kivAIhyfHilFR61RGL+GPXQ2MWZWFYbAGjyiYJnAmCP3NOTd0jMZEnDkbUvxhMmBYSdETk1rRgm+R4LOzFUGaHqHDLKLX+FIPKcF96hrucXzcWyLbIbEgE98OHlnVYCzRdK8jlqm8tehUc9c9WhQ== vagrant insecure public key > $TARGET/home/vagrant/.ssh/authorized_keys

# Fix permissions (important for ssh)
chroot $TARGET chown vagrant:vagrant /home/vagrant /home/vagrant/.ssh /home/vagrant/.ssh/authorized_keys
chmod 0600 $TARGET/home/vagrant/.ssh/authorized_keys
chmod 0700 $TARGET/home/vagrant/.ssh

# Set passwords as recommended for Vagrant. Insecure!
echo "vagrant:vagrant" | chroot $TARGET chpasswd
echo "root:vagrant" | chroot $TARGET chpasswd

# Passwordless sudo for Vagrant
echo "vagrant ALL=(ALL) NOPASSWD: ALL" > $TARGET/etc/sudoers.d/vagrant

###
# Set up things inside image for specific virtualization program

if [ "$FORMAT" = virtualbox ]; then
    chroot $TARGET apt-get update
    # Recommended packages would install VirtualBox X11 stuff we don't need
    chroot $TARGET apt-get install -y --no-install-recommends virtualbox-guest-dkms

    # Networking must work for Vagrant ssh port forwarding
    echo -e "auto enp0s3\nallow-hotplug enp0s3\niface enp0s3 inet dhcp" > $TARGET/etc/network/interfaces.d/enp0s3.cfg
fi

# Bring back original DNS
mv $TARGET/etc/resolv.conf.orig $TARGET/etc/resolv.conf

# Unmount image before conversion
chroot $TARGET apt-get clean
umount $TARGET/proc
umount $TARGET/dev
umount $TARGET
losetup -d /dev/loop0

###
# Create VM for requested virtualization software using image, and package it

mkdir -p $OUTPUT
if [ "$FORMAT" = virtualbox ]; then
    basefolder=/mnt/shared/output

    vbimage="$basefolder/$VMNAME/$VMNAME.vbi"
    vboxmanage createvm --basefolder /mnt/shared/output --name "$VMNAME" --ostype Ubuntu_64 --register
    vboxmanage modifyvm "$VMNAME" --memory 2048
    vboxmanage modifyvm "$VMNAME" --audio none
    vboxmanage modifyvm "$VMNAME" --nic1 NAT
    vboxmanage storagectl "$VMNAME" --name "SATA Controller" --add sata --portcount 1
    vboxmanage convertfromraw "$TEMPIMG" "$vbimage"
    vboxmanage storageattach "$VMNAME" --storagectl "SATA Controller" --type hdd --port 0 --medium "$vbimage"

    vagrant package --base "$VMNAME" --output "$DEST"

    vboxmanage unregistervm "$VMNAME" --delete
fi

###
# Common cleanup

rm $TEMPIMG
