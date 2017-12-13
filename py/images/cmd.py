import sys
from argparse import ArgumentParser, REMAINDER
from . import setup
from . import tools
from .builders.cloud import Builder_cloud


def build_image():
    parser = ArgumentParser()
    parser.add_argument('flavor', choices=setup.FLAVOURS.keys())
    parser.add_argument('--tags', default=None)
    parser.add_argument('--skip-tags', default=None)
    parser.add_argument('--no-apps', action='store_false', dest='apps')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('--image', default=None)
    parser.add_argument('--image-size', default='8G')
    options = parser.parse_args()
    tools.DEBUG = options.debug
    setup.build(
        options.flavor,
        options.tags,
        options.skip_tags,
        options.apps,
        options.image,
        options.image_size,
    )


def install():
    parser = ArgumentParser()
    parser.add_argument('--tags', default=None)
    options = parser.parse_args()
    setup.install(options.tags, options.skip_tags)


def run_with_image_chroot():
    parser = ArgumentParser()
    parser.add_argument('image', help="Path to the image")
    parser.add_argument('cmd', nargs=REMAINDER)
    options = parser.parse_args()

    builder = Builder_cloud()
    with builder.open_target(options.image) as target:
        print('+', ' '.join(options.cmd), file=sys.stderr)
        target.chroot_run(options.cmd)
