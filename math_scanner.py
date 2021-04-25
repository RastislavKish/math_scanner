#!/usr/bin/python3

import os, sys
from os import path

from imageio import imread
from PIL import Image, ImageOps
import pytesseract
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

    def __init__(self, scale_factor=1, invert=False, grayscale=False, blackwhite_threshold=-1):

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

class CharacterBox:

    @property
    def character(self): return self._character

    @property
    def top_left_x(self): return self._top_left_x

    @property
    def top_left_y(self): return self._top_left_y

    @property
    def bottom_right_x(self): return self._bottom_right_x

    @property
    def bottom_right_y(self): return self._bottom_right_y

    @property
    def height(self):
        return abs(self._top_left_y-self._bottom_right_y)

    @property
    def width(self):
        return abs(self._bottom_right_x-self._top_left_x)

    def __init__(self, character, top_left_x, top_left_y, bottom_right_x, bottom_right_y):

        self._character=character
        self._top_left_x=top_left_x
        self._top_left_y=top_left_y
        self._bottom_right_x=bottom_right_x
        self._bottom_right_y=bottom_right_y
    def from_list(l):
        if len(l)>=5:
            return CharacterBox(l[0], int(l[1]), int(l[2]), int(l[3]), int(l[4]))
        else:
            raise ValueError(f"CharacterBox can't be constructed from list of {len(l)} elements.")

    def is_on_line(self, line_y):
        return True if line_y>=self._top_left_y and line_y<=self._bottom_right_y else False

def segment_image(image):

    # First, recognize the input image and parse the bounding boxes of individual characters

    boxes=pytesseract.image_to_boxes(image, lang="slk")
    characters=[CharacterBox.from_list(i.split(" ")[:5]) for i in boxes.split("\n") if len(i.split(" "))==6]
    if len(characters)==0:
        return []

    # As we have the list of boxes, we need to find the smallest width of an alphanumerical character to get the threshold for detecting spaces

    alphanumerical_characters="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    space_width=10

    # Now, we can sort characters to lines. We will repeatedly pick one alphanumerical character and determine position of horizontal axis crossing it in middle. Then, we'll find all characters crossed by this axe and append them to the same line.

    lines={}

    while len(characters)>0:

        ch=None

        for i in range(len(characters)):
            if characters[i].character in alphanumerical_characters:
                ch=characters[i]
                del characters[i]
                break

        if ch==None:
            break

        line_y=ch.bottom_right_y-int(ch.height/2)

        lines[line_y]=[ch]

        # We need to use a while cycle instead of for, as for driving variables are immutable
        i=0
        while i<len(characters):
            if characters[i].is_on_line(line_y):
                lines[line_y].append(characters[i])
                del characters[i]
                i-=1
            i+=1

    # Some characters, such as commas or periods have smaller  boxes and therefore could be missed by the middle axes of bigger characters. Thus, they need to be assigned to the nearest available line

    for ch in characters:

        ch_middle_line=ch.top_left_y+int(ch.height/2)

        min_delta=None
        min_delta_key=None

        for key in lines.keys():
            delta=abs(key-ch_middle_line)

            if min_delta==None or delta<min_delta:
                min_delta=delta
                min_delta_key=key

        # We need to prevent inclusion of characters which are obviously not part of the line and got missed simply because they weren't part of any line. The distance shouldn't be bigger than the character itself.

        if min_delta<=3*ch.height:
            lines[min_delta_key].append(ch)
    ch=[] # Processed characters were not removed in the previous operation, so we clear the field to avoid any future confusion

    # We need to sort characters in individual lines

    for key in lines.keys():
        lines[key].sort(key=lambda i: i.top_left_x+int(i.width/2))

    # And now add spaces

    for line in lines.values():

        # We again have to deal with Python's inability to modify for driver variable

        i=0
        while i<len(line)-1:
            ch_1=line[i]
            ch_2=line[i+1]

            characters_distance=ch_2.top_left_x-ch_1.bottom_right_x

            if characters_distance>=space_width:
                space_character=CharacterBox(" ", ch_1.bottom_right_x, ch_1.top_left_y, ch_2.top_left_x, ch_2.bottom_right_y)
                line.insert(i+1, space_character)

                i+=1

            i+=1

    print(len(lines.keys()))
    for key in lines.keys():
        line=""
        for ch in lines[key]:
            line+=ch.character
        print(line)

ipc=ImageProcessingConfiguration()
img=ImageProcessor.load_image_from_file("img.png")
#print(pytesseract.image_to_string(ImageProcessor.process_image(img, ipc), lang="slk"))
segment_image(img)

