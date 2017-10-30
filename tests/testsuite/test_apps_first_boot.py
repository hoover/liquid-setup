from pathlib import Path
import pytest

FIRST_BOOT_STATUS_PATH = '/opt/common/first_boot_status'

def get_first_boot_status():
    with open(FIRST_BOOT_STATUS_PATH, 'r') as f:
        lines = f.readlines()
    status = []
    for line in lines:
        [path, return_value_str] = line.rsplit(" ", 1)
        return_value = int(return_value_str)
        script_name = Path(path).name
        status.append((script_name, return_value == 0))
    return status

# Used to move this information into the XML reports
@pytest.mark.parametrize("script,success", get_first_boot_status())
def test_app_first_boot(script, success):
    # TODO print supervisor logs and first boot logs for each
    # failed build.
    assert success
