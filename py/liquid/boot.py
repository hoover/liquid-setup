import os
from pathlib import Path
import subprocess

common = Path('/opt/common')
first_boot_done = common / 'first_boot_done'
first_boot_failed = common / 'first_boot_failed'


def sh(cmd, **kwargs):
    print('+', cmd)
    return subprocess.run(cmd, shell=True, check=True, **kwargs)


def on_boot():
    os.chdir(str(common))

    print("Starting firewall")
    sh('./libexec/firewall')

    if not (first_boot_done.is_file() or first_boot_failed.is_file()):
        print("Starting first boot.")
        try:
            sh('./initialize.sh')

        except subprocess.CalledProcessError:
            print("First boot failed.")
            first_boot_failed.touch()

        else:
            print("First boot done.")
            first_boot_done.touch()

    else:
        print("Not starting first boot, already done.")


    print("Starting all services.")
    # TODO: only start enabled services
    sh('supervisorctl start all')

    print("Running on-boot hook.")
    for file in Path('/opt/common/hooks/on-boot.d').iterdir():
        sh(str(file))

    print("Boot scripts done.")
