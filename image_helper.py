import time
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
class ImageHelper(object):
    """
    docstring for ImageHelper
    ---------
    Variables
    ---------

    ---------
    Functions
    ---------
    * capture_image
    * save_image
    * fetch_bot_meta_data
    * tag_bot_meta_data

    """

    def __init__(self):
        super(, self).__init__()
    @staticmethod
    def capture_image(pixel_width = 500,
                      pixel_height = 500,
                      slam):
        mapbytes = bytearray(pixel_width * pixel_height)
        img = [[0 for x in range(pixel_width)] for y in range(pixel_height)]
        slam.getmap(mapbytes)
        for row_num in range(0, pixel_width):
            start = row_num * pixel_width
            end = start + pixel_width
            img[row_num] = mapbytes[start:end]
        return img

    @staticmethod
    def save_image(img, filepath='./room_images/', filename= "test"):
        plt.ion()
        plt.gray()
        plt.imshow(img)
        ts = time.time()
        ts_str = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M%S')
        plt.savefig(filepath+ filename + ts_str +'.png')
