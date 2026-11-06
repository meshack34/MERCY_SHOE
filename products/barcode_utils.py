
from io import BytesIO

import barcode
from barcode.writer import ImageWriter

from django.core.files.base import ContentFile


def generate_barcode_image(product_variant):

    barcode_class = barcode.get_barcode_class('code128')

    barcode_object = barcode_class(
        product_variant.barcode,
        writer=ImageWriter()
    )

    buffer = BytesIO()

    barcode_object.write(
        buffer,
        options={
            'module_width': 0.3,
            'module_height': 15,
            'font_size': 10,
            'text_distance': 5,
            'quiet_zone': 6,
        }
    )

    filename = f"{product_variant.barcode}.png"

    product_variant.barcode_image.save(
        filename,
        ContentFile(buffer.getvalue()),
        save=True
    )

    buffer.close()
