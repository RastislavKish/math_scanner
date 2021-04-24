#!/usr/bin/python3

import os, sys
from os import path

from imageio import imread
from PIL import Image, ImageOps
import yaml

class ImageProcessor:

    def load_image_from_file(path):
        return Image.fromarray(imread(path, pilmode="RGB"))
    def process_image(image, config):

        if config.scale_factor!=1:
            image=ImageProcessor._scale(image, config.scale_factor)
        if config.invert:
            image=ImageOps.invert(image)
        if config.grayscale:
            image=ImageOps.grayscale(image)
        if config.blackwhite_threshold>=0 and config.blackwhite_threshold<256:
            image=ImageProcessor._blackwhite(image, config.blackwhite_threshold)

        return image
    def process_image_parameterized(image, scale_factor=1, invert=False, grayscale=False, blackwhite_threshold=-1):

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
class ImageProcessingConfiguration:

    def __init__(self, scale_factor=1, invert=1, grayscale=1, blackwhite_threshold=-1):

        self.scale_factor=scale_factor
        self.invert=invert
        self.grayscale=grayscale
        self.blackwhite_threshold=blackwhite_threshold

    def set_scale_factor(self, scale_factor):
        self.scale_factor=scale_factor
    def set_invert(self, invert):
        self.invert=invert
    def set_grayscale(self, grayscale):
        self.grayscale=grayscale
    def set_blackwhite_threshold(self, blackwhite_threshold):
        self.blackwhite_threshold=blackwhite_threshold
class TesseractConfiguration:

    def __init__(self, data_directory="/usr/share/tesseract-ocr/4.00/tessdata", recognition_language="eng", ocr_engine_mode=3):
        self.data_directory=data_directory
        self.recognition_language=recognition_language
        self.ocr_engine_mode=ocr_engine_mode

    def set_data_directory(self, data_directory):
        self.data_directory=data_directory
    def set_recognition_language(self, recognition_language):
        self.recognition_language=recognition_language
    def set_ocr_engine_mode(self, ocr_engine_mode):
        self.ocr_engine_mode=ocr_engine_mode

class Settings:

    def __init__(self):

        self.input_image_processing_configuration=ImageProcessingConfiguration()

        self._setting_getter_result=None # A helper variable for retrieving settings from configuration file

    def load(self, file_path):

        if path.isfile(file_path):
            doc=yaml.safe_load(open(file_path, "r", encoding="utf-8"))

            if self._get_tesseract_configuration(doc, "tesseract"): self.tesseract_configuration=self._setting_getter_result
            if self._get_image_processing_configuration(doc, "input image processing"): self.input_image_processing_configuration=self._setting_getter_result

    def _get_image_processing_configuration(self, yaml_node, key_name):
        if key_name in yaml_node:
            result=ImageProcessingConfiguration()
            ipc_node=yaml_node[key_name]

            if self._get_int(ipc_node, "scale factor"): result.set_scale_factor(self._setting_getter_result)
            if self._get_bool(ipc_node, "invert"): result.set_invert(self._setting_getter_result)
            if self._get_bool(ipc_node, "grayscale"): result.set_grayscale(self._setting_getter_result)
            if self._get_bool(ipc_node, "blackwhite"):
                if self._setting_getter_result==True:
                    if self._get_int(ipc_node, "blackwhite threshold"): result.set_blackwhite_threshold(self._setting_getter_result)
                else:
                    result.set_blackwhite_threshold(-1)

            self._setting_getter_result=result

            return True

        return False
    def _get_tesseract_configuration(self, yaml_node, key_name):
        if key_name in yaml_node:
            result=TesseractConfiguration()
            tc_node=yaml_node[key_name]

            if self._get_str(tc_node, "data directory"): result.set_data_directory(self._setting_getter_result)
            if self._get_str(tc_node, "recognition language"): result.set_recognition_language(self._setting_getter_result)
            if self._get_int(tc_node, "ocr engine mode"): result.set_ocr_engine_mode(self._setting_getter_result)

            self._setting_getter_result=result

            return True

        return False
    def _get_bool(self, yaml_node, key_name):
        if key_name in yaml_node and isinstance(yaml_node[key_name], bool):
            self._setting_getter_result=yaml_node[key_name]
            return True

        return False
    def _get_int(self, yaml_node, key_name):
        if key_name in yaml_node and isinstance(yaml_node[key_name], int):
            self._setting_getter_result=yaml_node[key_name]
            return True

        return False
    def _get_str(self, yaml_node, key_name):
        if key_name in yaml_node and isinstance(yaml_node[key_name], str):
            self._setting_getter_result=yaml_node[key_name]
            return True

        return False

