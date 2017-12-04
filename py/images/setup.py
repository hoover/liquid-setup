from pathlib import Path
from .builders.cloud import Builder_cloud
from .builders.odroid import Builder_odroid_c2, Builder_odroid_xu4

FLAVOURS = {
    'cloud': Builder_cloud,
    'odroid_c2': Builder_odroid_c2,
    'odroid_xu4': Builder_odroid_xu4,
}


def build(flavor, tags, skip_tags, image_path):
    builder_cls = FLAVOURS[flavor]
    builder = builder_cls()
    builder.install_ansible()

    if image_path:
        image = Path(image_path).resolve()

    else:
        builder.install_qemu_utils()
        image = builder.prepare_image()

    builder.build(image, tags, skip_tags)


def install(tags, skip_tags):
    builder = Builder_cloud()
    (builder.setup / 'ansible' / 'vars' / 'config.yml').touch()
    (builder.setup / 'ansible' / 'vars' / 'liquidcore.yml').touch()
    builder.run_ansible('liquid.yml', tags, skip_tags)
