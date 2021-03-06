import subprocess
import re

from ..tools import download, xzcat, run
from .base import BaseBuilder, Platform, IMAGES


class Platform_rock64(Platform):

    offset = 134217728

    def get_base_image(self):
        base_image_url = (
            'https://jenkins.liquiddemo.org/__images__/base/'
            'xenial-minimal-rock64-0.5.15-136-arm64.img.xz'
        )
        base_image = IMAGES / 'xenial-rock64-minimal.img.xz'
        download(base_image_url, base_image)

        image = IMAGES / 'ubuntu-rock64-raw.img'
        xzcat(base_image, image)

        return image

    def get_root_fs_size(self, image):
        def get_sector_size(image):
            fdisk_output = (
                run(['/sbin/fdisk', '-l', str(image)], stdout=subprocess.PIPE)
                .stdout.decode('latin1')
                .splitlines(keepends=True)
            )
            for line in fdisk_output:
                m = re.search(r'^Sector size.*\s+(?P<sector>\d+) bytes$', line)
                if m:
                    return int(m.group('sector'))


        def get_size_in_sectors(image):
            sfdisk_output = (
                run(['/sbin/sfdisk', '-d', str(image)], stdout=subprocess.PIPE)
                .stdout.decode('latin1')
                .splitlines(keepends=True)
            )
            for line in sfdisk_output:
                m = re.search(r'size=\s*(?P<size>\d+).*name="root"', line)
                if m:
                    return int(m.group('size'))

        return get_size_in_sectors(image) * get_sector_size(image)


class Builder_rock64(BaseBuilder):

    platform = Platform_rock64()

    def resize_partition(self, image, new_size):
        run(['truncate', '-s', new_size, str(image)])

        run(['apt-get', '-qq', 'install', '-y', 'gdisk'],
            stdout=subprocess.DEVNULL)
        run(['sgdisk', '-e', str(image)])

        sfdisk_orig = (
            run(['sfdisk', '-d', str(image)], stdout=subprocess.PIPE)
            .stdout.decode('latin1')
            .splitlines(keepends=True)
        )

        sfdisk_new = []
        for line in sfdisk_orig:
            if 'name="root"' in line:
                line = re.sub(r'size=[^,]+,', '', line)
            sfdisk_new.append(line)

        run(['sfdisk', str(image)], input=''.join(sfdisk_new).encode('latin1'))
