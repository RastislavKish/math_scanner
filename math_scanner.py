#!/usr/bin/python3

import sys

from imageio import imread
from PIL import Image, ImageOps

class ImageProcessor:

    def load_image_from_file(path):
        return Image.fromarray(imread(path, pilmode="RGB"))
    def process_image(image, scale_factor=1, invert=False, grayscale=False, blackwhite_threshold=-1):

        if scale_factor!=1:
            image=ImageProcessor._scale(image, scale_factor)
        if invert:
            image=ImageOps.invert(image)
        if grayscale:
            image=ImageOps.grayscale(image)
        if blackwhite_threshold>=0 and blackwhite_threshold<256:
            image=ImageProcessor._blackwhite(image, blackwhite_threshold)

        return image

    def _scale(image, scale_factor):
        width, height=image.size

        return image.resize((width*scale_factor, height*scale_factor), Image.BICUBIC)
    def _blackwhite(image, threshold):
        return ImageOps.grayscale(image).point(lambda p: 0 if p<threshold else 255)

