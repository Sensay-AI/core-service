import logging
from PIL import Image

logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p'
)

logger = logging.getLogger(__name__)


def get_image_storage_size(image_bytes):
    with Image.open(image_bytes) as img:
        storage_size = len(img.fp.read())
    return storage_size
