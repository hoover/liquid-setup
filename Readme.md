# Liquid Investigations: Software Stack Setup
This repository contains [ansible](http://docs.ansible.com/ansible/) scripts
that set up the software stack for [liquid investigations][]. It's designed to
work in two scenarios: installation on a server or VPS, and preparing an OS
image for a cloud server or ARM64 microboard.

[liquid investigations]: https://liquidinvestigations.org/wordpress


### Build an OS image
You can build a full system image, based on Ubuntu 16.04 LTS, that includes the
liquid software bundle. This is done using [buildbot][].

[buildbot]: https://github.com/liquidinvestigations/buildbot

First, set up buildbot and make sure you can log into an instance. It should be
an arm64 instance running on arm64 hardware if you want to target a microboard,
or an x86_64 image running on x86_64 hardware if you want a server/cloud image.

Next, clone this repository inside the `shared` folder, and run the build
script in a buildbot instance (use `build-odroid_c2-image.sh for an odroid
arm64 image instead of an x86_64 image):

```shell
$ git clone https://github.com/liquidinvestigations/setup ./shared/setup
$ echo 'liquid_domain: liquid.example.com' > ./shared/setup/ansible/vars/config.yml
$ ./buildbot run shared/setup/bin/build-x86_64-image.sh
```

If all goes well, the image should be saved in the `shared/output` folder.

#### Convert the image
The build scripts produce "raw" images. You can convert them to VMware or
VirtualBox format. Append `-p` to get progress report.

```sh
qemu-img convert liquid-20170627-x86_64.img -O vmdk liquid-20170627-x86_64.vmdk
qemu-img convert liquid-20170627-x86_64.img -O vmi liquid-20170627-x86_64.vmi
```



### Set up on existing server
These instructions assume Ubuntu 16.04 LTS. They work on Debian systems with
some adaptations, YMMV.

```shell
$ add-apt-repository ppa:ansible/ansible -y # for Ansible 2.2 or newer
$ apt-get update
$ apt install ansible -y
$ cd /opt
$ git clone https://github.com/liquidinvestigations/setup
$ cd setup/ansible
$ echo 'liquid_domain: liquid.example.com' > ./vars/config.yml
$ ansible-playbook server.yml
```


## First boot
On first (re)boot, the bundle will configure databases, and import the
[testdata](https://github.com/hoover/testdata) collection into Hoover. This
will take a few minutes. You can follow the progress in the log file:

```
tail -f /var/log/rc.local.log
```

When the initialization scripts compete successfully, they will create the file
`/opt/common/first_boot_done`, so they don't run on the next boot.

### hotspot
On ARM system images, after the first-boot scripts complete, the system will
attempt to create a wireless hotspot, if it detecs any AP-capable wireless
interfaces. The SSID is `liquid`, password `chocolate`.

### Hoover and Hypothesis
Hoover and Hypothesis are started after first boot setup and automatically
started on subsequent boots.

They are accessible at subdomains of `liquid_domain` which was set above:
http://hoover.liquid.example.com and http://hypothesis.liquid.example.com
When running from a VM you may need to set up the VM network configuration
and put those hosts in your hosts file.

The services can be managed via `supervisorctl`.
