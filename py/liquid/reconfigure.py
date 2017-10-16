import sys
import json
from pathlib import Path
from images.setup import install

ANSIBLE_VARS = Path(__file__).parent.parent.parent / 'ansible' / 'vars'


def on_reconfigure():
    options = json.load(sys.stdin)

    vars = {
        'liquidcore': options['vars'],
    }

    vars_path = ANSIBLE_VARS / 'liquidcore.yml'
    with vars_path.open('w', encoding='utf8') as f:
        print(json.dumps(vars, indent=2, sort_keys=True), file=f)

    install(tags='configure')
