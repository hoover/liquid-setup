import re
from pathlib import Path
from contextlib import contextmanager
import subprocess
from ..tools import run, losetup, mount_target

IMAGES = Path('/mnt/images')


class Platform:

    def get_base_image(self):
        raise NotImplementedError


@contextmanager
def patch_resolv_conf(target):
    resolv_conf = target.mount_point / 'etc' / 'resolv.conf'
    resolv_conf_orig = resolv_conf.with_name(resolv_conf.name + '.orig')

    resolv_conf.rename(resolv_conf_orig)
    with resolv_conf.open('wb') as dst:
        dst.write(b"nameserver 8.8.8.8\n")

    try:
        yield

    finally:
        resolv_conf_orig.rename(resolv_conf)


class BaseBuilder:

    setup = Path(__file__).resolve().parent.parent.parent.parent

    def install_ansible(self):
        have_ansible = (
            run(['which', 'ansible-playbook'],
                stdout=subprocess.PIPE, check=False)
            .stdout.strip()
        )
        if not have_ansible:
            run(['apt-add-repository', '-y', 'ppa:ansible/ansible'])
            run(['apt-get', '-qq', 'update'], stdout=subprocess.DEVNULL)
            run(['apt-get', '-qq', 'install', '-y', 'ansible', 'git'],
                stdout=subprocess.DEVNULL)

    def install_qemu_utils(self):
        run(['apt-get', '-qq', 'install', '-y', 'qemu-utils'],
            stdout=subprocess.DEVNULL)

    def resize_partition(self, image, new_size):
        run(['truncate', '-s', new_size, str(image)])

        sfdisk_orig = (
            run(['sfdisk', '-d', str(image)], stdout=subprocess.PIPE)
            .stdout.decode('latin1')
            .splitlines(keepends=True)
        )

        sfdisk_new = []
        for line in sfdisk_orig:
            if 'type=83' in line:
                line = re.sub(r'size=[^,]+,', '', line)
            sfdisk_new.append(line)

        run(['sfdisk', str(image)], input=''.join(sfdisk_new).encode('latin1'))

    @contextmanager
    def open_target(self, image):
        mount_point = Path('/mnt/target')
        mount_point.mkdir(parents=True, exist_ok=True)

        with losetup(image, self.platform.offset) as device:
            with mount_target(device, mount_point, ['proc', 'dev']) as target:
                with patch_resolv_conf(target):
                    yield target

    def prepare_chroot(self, target):
        apt_conf_liquid = target.mount_point / 'etc/apt/apt.conf.d/liquid'
        with apt_conf_liquid.open('w', encoding='utf8') as f:
            print('APT::Install-Recommends "false";', file=f)
            print('APT::Install-Suggests "false";', file=f)

        target.chroot_run(['apt-get', '-qq', 'update'])
        target.chroot_run(['apt-get', '-qq', 'install', '-y', 'python'],
                          stdout=subprocess.DEVNULL)
        target.chroot_run(['apt-get', '-qq', 'clean'])

    def run_ansible(self, playbook, tags=None):
        cmd = ['ansible-playbook', '-i', 'hosts', playbook]
        if tags:
            cmd += ['--tags', tags]
        run(cmd, cwd=str(self.setup / 'ansible'))

    def prepare_image(self):
        image = self.platform.get_base_image()
        self.resize_partition(image, '8G')

        with self.open_target(image) as target:
            run(['resize2fs', target.device])
            self.prepare_chroot(target)

        return image

    def build(self, image, tags):
        with self.open_target(image) as target:
            self.run_ansible('image_chroot.yml', tags)
