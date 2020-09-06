import stringcase
import os
import time

from PIL import Image

def convert_to_order():
    # TODO
    pass


def capitaliseName(name):
    return stringcase.capitalcase(name)


def formatToCurrency(amount):
    return "{:.2f}".format(float(amount))



def upload_picture(uploaded_picture):
    f_name, f_ext = os.path.splitext(uploaded_picture.filename)
    image_name = f_name + str(round(time.time())) + f_ext
    # image_path = os.path.join(app.root_path, 'static/images', image_name)
    image_path = 'freshpicks/static/images/' + image_name.replace(" ", "")
    resize = (300, 300)
    resize_image = Image.open(uploaded_picture)
    resize_image.thumbnail(resize)
    resize_image.save(image_path)
    image_path = image_path.replace("freshpicks", "")
    return image_path