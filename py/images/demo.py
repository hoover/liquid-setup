import re
from pathlib import Path
from contextlib import contextmanager
from .builders.cloud import Builder_cloud
from .tools import run

SETUP_GIT = 'https://github.com/liquidinvestigations/setup'

class DemoBuilder(Builder_cloud):

    def create_swapfile(self, target):
        swap_size_gb = 1
        swap_rel = 'var/local/swap1'
        swapfile = target.mount_point / swap_rel

        if swapfile.exists():
            print("swapfile exists; skipping")
            return

        print("creating {}GB swap file".format(swap_size_gb))
        run([
            'dd',
            'if=/dev/zero',
            'of={}'.format(swapfile),
            'bs=1M',
            'count={}'.format(1024 * swap_size_gb),
        ])

        run(['mkswap', str(swapfile)])

        target_fstab = target.mount_point / 'etc/fstab'
        with target_fstab.open('a', encoding='utf8') as f:
            f.write('/{} none swap sw 0 0\n'.format(swap_rel))

    def setup_network(self, target):
        ens3_cfg = target.mount_point / 'etc/network/interfaces.d/ens3.cfg'
        with ens3_cfg.open('w', encoding='utf8') as f:
            f.write('auto ens3\niface ens3 inet dhcp\n')

    def setup_console(self, target):
        grub_files = [
            'boot/grub/grub.cfg',
            'etc/default/grub',
            'etc/default/grub.d/50-cloudimg-settings.cfg',
        ]
        for rel_path in grub_files:
            path = target.mount_point / rel_path
            run(['sed', '-i ', 's/console=tty1/console=ttyS0/g', str(path)])

    def setup_ansible(self, target, config_yml):
        if not Path('/usr/bin/ansible-playbook').is_file():
            self.install_ansible()
            self.install_qemu_utils()

        setup_path = target.mount_point / 'opt' / 'setup'
        target_config_yml = setup_path / 'ansible/vars/config.yml'
        with config_yml.open(encoding='utf8') as f:
            with target_config_yml.open('w', encoding='utf8') as g:
                g.write(f.read())

        run([
            'ansible-playbook',
            '-i', 'hosts',
            'liquid.yml',
        ], cwd=str(setup_path / 'ansible'))

    def kill_testdata(self, target):
        import_testdata = (
            target.mount_point /
            'opt/hoover/libexec/import_testdata'
        )
        with import_testdata.open('w') as f:
            f.write('#!/bin/bash\necho "no testdata"\n')

    def copy_users(self, target, users_json):
        target_users_json = target.mount_point / 'opt/liquid-core/users.json'
        with users_json.open('rb') as f:
            with target_users_json.open('wb') as g:
                g.write(f.read())

    def setup_demo(self, image, config_yml, users_json, shell, no_testdata, serial):
        with self.open_target(image) as target:
            if shell:
                run(['bash'], cwd=str(target.mount_point))
                return
            self.create_swapfile(target)
            self.setup_network(target)
            if serial:
                self.setup_console(target)
            self.setup_ansible(target, config_yml)
            self.copy_users(target, users_json)
            if no_testdata:
                self.kill_testdata(target)

def install():
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Provision a nightly image as demo server")
    parser.add_argument('image', help="Path to the image")
    parser.add_argument('config_yml', help="Path to ansible configuration file")
    parser.add_argument('users_json', help="Path to JSON file with initial users")
    parser.add_argument('--shell', action='store_true', help="Open shell in chroot")
    parser.add_argument('--no-testdata', action='store_true', help="Skip testdata")
    parser.add_argument('--serial', action='store_true',
                        help="Use ttys0 as serial console")
    options = parser.parse_args()

    builder = DemoBuilder()
    builder.setup_demo(
        Path(options.image).resolve(),
        Path(options.config_yml),
        Path(options.users_json),
        options.shell,
        options.no_testdata,
        options.serial,
    )
