#!/usr/bin/python3

from base64 import b64encode
from io import BytesIO
import json
from os import path
import requests

import appdirs
from PIL import Image, ImageOps
from speechd.client import SSIPClient
import pytesseract
import wx
import yaml

class ImageProcessor:

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
class MathpixConfiguration:

    def __init__(self, app_id=None, app_key=None):

        self.app_id=app_id
        self.app_key=app_key

    def set_app_id(self, app_id):
        if app_id=="your_app_id":
            self.app_id=None
        else:
            self.app_id=app_id
    def set_app_key(self, app_key):
        if app_key=="your_app_id":
            self.app_key=None
        else:
            self.app_key=app_key
class SpeechConfiguration:

    def __init__(self, speech_module="espeak-ng", language="en", voice="male1", punctuation_mode="some", pitch=10, rate=2, volume=100):

        self.speech_module=speech_module
        self.language=language
        self.voice=voice
        self.punctuation_mode=punctuation_mode
        self.pitch=pitch
        self.rate=rate
        self.volume=volume

    def set_speech_module(self, speech_module):
        self.speech_module=speech_module
    def set_language(self, language):
        self.language=language
    def set_voice(self, voice):
        self.voice=voice
    def set_punctuation_mode(self, punctuation_mode):
        self.punctuation_mode=punctuation_mode
    def set_pitch(self, pitch):
        self.pitch=pitch
    def set_rate(self, rate):
        self.rate=rate
    def set_volume(self, volume):
        self.volume=volume
class TesseractConfiguration:

    def __init__(self, data_directory="", recognition_language="eng", ocr_engine_mode=3):
        self.data_directory=data_directory
        self.recognition_language=recognition_language
        self.ocr_engine_mode=ocr_engine_mode

    def set_data_directory(self, data_directory):
        self.data_directory=data_directory if data_directory!="default" else ""
    def set_recognition_language(self, recognition_language):
        self.recognition_language=recognition_language
    def set_ocr_engine_mode(self, ocr_engine_mode):
        self.ocr_engine_mode=ocr_engine_mode

class Settings:

    def __init__(self):

        self.mathpix_configuration=MathpixConfiguration()
        self.tesseract_configuration=TesseractConfiguration()
        self.input_image_processing_configuration=ImageProcessingConfiguration()
        self.speech_configuration=SpeechConfiguration()

        self._setting_getter_result=None # A helper variable for retrieving settings from configuration file

    def load(self, file_path):

        if path.isfile(file_path):
            doc=yaml.safe_load(open(file_path, "r", encoding="utf-8"))

            if self._get_mathpix_configuration(doc, "mathpix"): self.mathpix_configuration=self._setting_getter_result
            if self._get_tesseract_configuration(doc, "tesseract"): self.tesseract_configuration=self._setting_getter_result
            if self._get_image_processing_configuration(doc, "input image processing"): self.input_image_processing_configuration=self._setting_getter_result
            if self._get_speech_configuration(doc, "speech"): self.speech_configuration=self._setting_getter_result

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
    def _get_mathpix_configuration(self, yaml_node, key_name):
        if key_name in yaml_node:
            result=MathpixConfiguration()
            mathpix_node=yaml_node[key_name]

            if self._get_str(mathpix_node, "app id"): result.set_app_id(self._setting_getter_result)
            if self._get_str(mathpix_node, "app key"): result.set_app_key(self._setting_getter_result)

            self._setting_getter_result=result

            return True

        return False
    def _get_speech_configuration(self, yaml_node, key_name):
        if key_name in yaml_node:
            result=SpeechConfiguration()
            speech_node=yaml_node[key_name]

            if self._get_str(speech_node, "speech module"): result.set_speech_module(self._setting_getter_result)
            if self._get_str(speech_node, "language"): result.set_language(self._setting_getter_result)
            if self._get_str(speech_node, "voice"): result.set_voice(self._setting_getter_result)
            if self._get_str(speech_node, "punctuation mode"): result.set_punctuation_mode(self._setting_getter_result)
            if self._get_int(speech_node, "pitch"): result.set_pitch(self._setting_getter_result)
            if self._get_int(speech_node, "rate"): result.set_rate(self._setting_getter_result)
            if self._get_int(speech_node, "volume"): result.set_volume(self._setting_getter_result)

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
    def bottom_left_x(self): return self._bottom_left_x

    @property
    def bottom_left_y(self): return self._bottom_left_y

    @property
    def top_right_x(self): return self._top_right_x

    @property
    def top_right_y(self): return self._top_right_y

    @property
    def height(self):
        return abs(self._top_right_y-self._bottom_left_y)

    @property
    def width(self):
        return abs(self._top_right_x-self._bottom_left_x)

    def __init__(self, character, bottom_left_x, bottom_left_y, top_right_x, top_right_y):

        self._character=character
        self._bottom_left_x=bottom_left_x
        self._bottom_left_y=bottom_left_y
        self._top_right_x=top_right_x
        self._top_right_y=top_right_y
    def from_list(l):
        if len(l)>=5:
            return CharacterBox(l[0], int(l[1]), int(l[2]), int(l[3]), int(l[4]))
        else:
            raise ValueError(f"CharacterBox can't be constructed from list of {len(l)} elements.")

    def is_on_line(self, line_y):
        return line_y>=self._bottom_left_y and line_y<=self._top_right_y

def segment_image(image):

    # First, recognize the input image and parse the bounding boxes of individual characters. We currently don't need the page number entry, so will take just the first 5 entries of each row of image_to_boxes.

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

        line_y=ch.bottom_left_y+int(ch.height/2)

        lines[line_y]=[ch]

        # We need to use a while cycle instead of for, as for driving variables are immutable
        i=0
        while i<len(characters):
            if characters[i].is_on_line(line_y):
                lines[line_y].append(characters[i])
                del characters[i]
                continue
            i+=1

    # Some characters, such as commas or periods have smaller  boxes and therefore could be missed by the middle axes of bigger characters. Thus, they need to be assigned to the nearest available line

    for ch in characters:

        ch_middle_line=ch.top_right_y-int(ch.height/2)

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
        lines[key].sort(key=lambda i: i.bottom_left_x+int(i.width/2))

    # And now add spaces

    for line in lines.values():

        # We again have to deal with Python's inability to modify for driver variable

        i=0
        while i<len(line)-1:
            ch_1=line[i]
            ch_2=line[i+1]

            characters_distance=ch_2.bottom_left_x-ch_1.top_right_x

            if characters_distance>=space_width:
                space_character=CharacterBox(" ", ch_1.top_right_x, ch_1.bottom_left_y, ch_2.bottom_left_x, ch_2.top_right_y)
                line.insert(i+1, space_character)

                i+=1

            i+=1

    result=[i for i in lines.keys()]
    result.sort(reverse=True)
    result=[lines[line] for line in result]

    return result

class MathpixRecognizer:

    def __init__(self, configuration=None):

        self._configuration=MathpixConfiguration()

        self.configure(configuration)

    def configure(self, configuration):
        if configuration!=None:
            self._configuration=configuration

    def recognize(self, image):

        assert self._configuration.app_id!=None
        assert self._configuration.app_key!=None

        png_stream=BytesIO()
        image.save(png_stream, format="png")
        png_stream.seek(0)

        png_b64=b64encode(png_stream.read()).decode("utf-8")

        png_stream.close()

        # We have the image in a base64 encoding, now it's time to call the server

        service="https://api.mathpix.com/v3/latex"

        headers={
            "app_id": self._configuration.app_id,
            "app_key": self._configuration.app_key,
            "Content-type": "application/json"
            }

        args=json.dumps({
            "src": f"data:image/png;base64,{png_b64}",
            "formats": ["asciimath"],
            })

        result=requests.post(service, headers=headers, data=args, timeout=30)

        return result.text

class MathScanner:

    @property
    def file_name(self): return self._file_name

    @property
    def image_boxes(self): return self._image_boxes

    @property
    def image_text(self): return self._image_text

    def __init__(self, settings):

        self._file_name="Untitled"
        self._image=None
        self._image_text=""
        self._image_boxes=[]

        self._left_border=None
        self._right_border=None
        self._top_border=None
        self._bottom_border=None

        self._settings=settings
        self._mathpix_recognizer=MathpixRecognizer(settings.mathpix_configuration)

    def load_image_from_file(self, path):
        self._image=ImageProcessor.process_image(Image.open(path), self._settings.input_image_processing_configuration)
        self._file_name=path.split("/")[-1]
        self._image_boxes=segment_image(self._image)
        self._image_text="\n".join(["".join([ch.character for ch in l]) for l in self._image_boxes])

        self._left_border, self._right_border, self._top_border, self._bottom_border=None, None, None, None

    def place_left_border(self, row, column):

        self._check_coordinates(row, column)

        border=self._image_boxes[row][column]._bottom_left_x

        if self._left_border==None or border<self._left_border:
            self._left_border=border

            return True

        return False
    def place_right_border(self, row, column):

        self._check_coordinates(row, column)

        border=self._image_boxes[row][column]._top_right_x

        if self._right_border==None or border>self._right_border:
            self._right_border=border

            return True

        return False
    def place_top_border(self, row, column):

        self._check_coordinates(row, column)

        border=self._image_boxes[row][column]._top_right_y

        if self._top_border==None or border>self._top_border:
            self._top_border=border

            return True

        return False
    def place_bottom_border(self, row, column):

        self._check_coordinates(row, column)

        border=self._image_boxes[row][column]._bottom_left_y

        if self._bottom_border==None or border<self._bottom_border:
            self._bottom_border=border

            return True

        return False

    def remove_left_border(self):
        if self._left_border!=None:
            self._left_border=None

            return True

        return False
    def remove_right_border(self):
        if self._right_border!=None:
            self._right_border=None

            return True

        return False
    def remove_top_border(self):
        if self._top_border!=None:
            self._top_border=None

            return True

        return False
    def remove_bottom_border(self):
        if self._bottom_border!=None:
            self._bottom_border=None

            return True

        return False

    def get_bordered_region(self):
        assert self._image!=None

        if self._left_border==None or self._right_border==None:
            left_border=self._left_border if self._left_border!=None else 0
            right_border=self._right_border if self._right_border!=None else self._image.size[0]-1
        else:
            left_border, right_border=(self._left_border, self._right_border) if self._left_border<self._right_border else (self._right_border, self._left_border)

        if self._top_border==None or self._bottom_border==None:
            top_border=self._top_border if self._top_border!=None else self._image.size[1]-1
            bottom_border=self._bottom_border if self._bottom_border!=None else 0
        else:
            top_border, bottom_border=(self._top_border, self._bottom_border) if self._top_border>self._bottom_border else (self._bottom_border, self._top_border)

        if left_border<0: left_border=0
        if right_border>=self._image.size[0]: right_border=self._image.size[0]-1
        if bottom_border<0: bottom_border=0
        if top_border>=self._image.size[1]: top_border=self._image.size[1]-1

        # Tesseract and PIL use different coordinates system. While Tesseract has its 0;0 point in bottom left corner, PIL uses the top left one. It's therefore needed to convert our values

        top_border=self._image.size[1]-1-top_border
        bottom_border=self._image.size[1]-1-bottom_border

        return self._image.crop((left_border, top_border, right_border+1, bottom_border+1))

    def recognize(self, image):
        return self._mathpix_recognizer.recognize(image)

    def _check_coordinates(self, row, column):

        if row<0 or row>=len(self._image_boxes):
            raise ValueError(f"Row {row} out of range, {len(self._image_boxes)} available.")
        if column<0 or column>=len(self._image_boxes[row]):
            raise ValueError(""f"Column {column} out of range, {len(self._image_boxes[row])} available.")

class LinuxSpeech:

    def __init__(self, configuration=None):
        self._connection=SSIPClient("math_scanner")

        self.configure(configuration)

    def configure(self, configuration):

        if self._connection!=None and configuration!=None:
            self._connection.set_output_module(configuration.speech_module)
            self._connection.set_language(configuration.language)
            self._connection.set_voice(configuration.voice)
            self._connection.set_punctuation(configuration.punctuation_mode)
            self._connection.set_pitch(configuration.pitch)
            self._connection.set_rate(configuration.rate)
            self._connection.set_volume(configuration.volume)

    def speak(self, text):
        self._connection.speak(text)

    def release(self):
        self._connection.close()
        self._connection=None

class MainWindow(wx.Frame):

    OPEN_MENU_ITEM_ID=1

    PLACE_LEFT_BORDER_MENU_ITEM_ID=31
    PLACE_RIGHT_BORDER_MENU_ITEM_ID=32
    PLACE_TOP_BORDER_MENU_ITEM_ID=33
    PLACE_BOTTOM_BORDER_MENU_ITEM_ID=34

    REMOVE_LEFT_BORDER_MENU_ITEM_ID=35
    REMOVE_RIGHT_BORDER_MENU_ITEM_ID=36
    REMOVE_TOP_BORDER_MENU_ITEM_ID=37
    REMOVE_BOTTOM_BORDER_MENU_ITEM_ID=38

    RECOGNIZE_BORDERED_REGION_MENU_ITEM_ID=71
    RECOGNIZE_FULL_IMAGE_MENU_ITEM_ID=72

    def __init__(self):
        super().__init__(parent=None)

        self._settings=Settings()
        self._settings.load(path.join(appdirs.user_config_dir("math_scanner"), "settings.yaml"))

        self._speech=LinuxSpeech(self._settings.speech_configuration)

        self._math_scanner=MathScanner(self._settings)

        self._setup_interface()

        self._set_window_title()
    def _setup_interface(self):

        self._image_text_TextCtrl=wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP)

        menu_bar=wx.MenuBar()
        menu_bar.Append(self._construct_file_menu(), "&File")
        menu_bar.Append(self._construct_borders_menu(), "&Borders")
        menu_bar.Append(self._construct_recognition_menu(), "&Recognition")
        menu_bar.Append(self._construct_help_menu(), "&Help")

        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_CLOSE, self._main_window_close)
    def _construct_file_menu(self):

        file_menu=wx.Menu()

        file_menu.Append(MainWindow.OPEN_MENU_ITEM_ID, "Open\tCtrl+O")
        file_menu.Append(wx.ID_EXIT, "Exit")

        self.Bind(wx.EVT_MENU, self._open_menu_item_click, id=MainWindow.OPEN_MENU_ITEM_ID)
        self.Bind(wx.EVT_MENU, self._exit_menu_item_click, id=wx.ID_EXIT)

        return file_menu
    def _construct_borders_menu(self):

        borders_menu=wx.Menu()

        borders_menu.Append(MainWindow.PLACE_LEFT_BORDER_MENU_ITEM_ID, "Place left border\tCtrl+L")
        borders_menu.Append(MainWindow.PLACE_RIGHT_BORDER_MENU_ITEM_ID, "Place right border\tCtrl+R")
        borders_menu.Append(MainWindow.PLACE_TOP_BORDER_MENU_ITEM_ID, "Place top border\tCtrl+T")
        borders_menu.Append(MainWindow.PLACE_BOTTOM_BORDER_MENU_ITEM_ID, "Place bottom border\tCtrl+B")

        borders_menu.Append(MainWindow.REMOVE_LEFT_BORDER_MENU_ITEM_ID, "Remove left border\tCtrl+Shift+L")
        borders_menu.Append(MainWindow.REMOVE_RIGHT_BORDER_MENU_ITEM_ID, "Remove right border\tCtrl+Shift+R")
        borders_menu.Append(MainWindow.REMOVE_TOP_BORDER_MENU_ITEM_ID, "Remove top border\tCtrl+Shift+T")
        borders_menu.Append(MainWindow.REMOVE_BOTTOM_BORDER_MENU_ITEM_ID, "Remove bottom border\tCtrl+Shift+B")

        # Events

        self.Bind(wx.EVT_MENU, self._place_left_border_menu_item_click, id=MainWindow.PLACE_LEFT_BORDER_MENU_ITEM_ID)
        self.Bind(wx.EVT_MENU, self._place_right_border_menu_item_click, id=MainWindow.PLACE_RIGHT_BORDER_MENU_ITEM_ID)
        self.Bind(wx.EVT_MENU, self._place_top_border_menu_item_click, id=MainWindow.PLACE_TOP_BORDER_MENU_ITEM_ID)
        self.Bind(wx.EVT_MENU, self._place_bottom_border_menu_item_click, id=MainWindow.PLACE_BOTTOM_BORDER_MENU_ITEM_ID)

        self.Bind(wx.EVT_MENU, self._remove_left_border_menu_item_click, id=MainWindow.REMOVE_LEFT_BORDER_MENU_ITEM_ID)
        self.Bind(wx.EVT_MENU, self._remove_right_border_menu_item_click, id=MainWindow.REMOVE_RIGHT_BORDER_MENU_ITEM_ID)
        self.Bind(wx.EVT_MENU, self._remove_top_border_menu_item_click, id=MainWindow.REMOVE_TOP_BORDER_MENU_ITEM_ID)
        self.Bind(wx.EVT_MENU, self._remove_bottom_border_menu_item_click, id=MainWindow.REMOVE_BOTTOM_BORDER_MENU_ITEM_ID)

        return borders_menu
    def _construct_recognition_menu(self):

        recognition_menu=wx.Menu()

        recognition_menu.Append(MainWindow.RECOGNIZE_BORDERED_REGION_MENU_ITEM_ID, "Recognize bordered region")
        recognition_menu.Append(MainWindow.RECOGNIZE_FULL_IMAGE_MENU_ITEM_ID, "Recognize full image")

        # Events

        self.Bind(wx.EVT_MENU, self._recognize_bordered_region_menu_item_click, id=MainWindow.RECOGNIZE_BORDERED_REGION_MENU_ITEM_ID)
        self.Bind(wx.EVT_MENU, self._recognize_full_image_menu_item_click, id=MainWindow.RECOGNIZE_FULL_IMAGE_MENU_ITEM_ID)

        return recognition_menu
    def _construct_help_menu(self):

        help_menu=wx.Menu()

        help_menu.Append(wx.ID_ABOUT, "About")

        return help_menu
    def _set_window_title(self):
        self.SetTitle(f"{self._math_scanner.file_name} - Math scanner")

    # Event methods

    def _open_menu_item_click(self, event):

        with wx.FileDialog(self, "Open an image", style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST) as file_dialog:

            if file_dialog.ShowModal()==wx.ID_CANCEL:
                return

            path=file_dialog.GetPath()

            self._open_image(path)
    def _exit_menu_item_click(self, event):
        self.Close()

    def _place_left_border_menu_item_click(self, event):
        _, column, row=self._image_text_TextCtrl.PositionToXY(self._image_text_TextCtrl.GetInsertionPoint())

        try:
            if self._math_scanner.place_left_border(row, column):
                self._speech.speak("Set")
        except ValueError:
            self._speech.speak("Invalid coordinates")
    def _place_right_border_menu_item_click(self, event):
        _, column, row=self._image_text_TextCtrl.PositionToXY(self._image_text_TextCtrl.GetInsertionPoint())

        try:
            if self._math_scanner.place_right_border(row, column):
                self._speech.speak("Set")
        except ValueError:
            self._speech.speak("Invalid coordinates")
    def _place_top_border_menu_item_click(self, event):
        _, column, row=self._image_text_TextCtrl.PositionToXY(self._image_text_TextCtrl.GetInsertionPoint())

        try:
            if self._math_scanner.place_top_border(row, column):
                self._speech.speak("Set")
        except ValueError:
            self._speech.speak("Invalid coordinates")
    def _place_bottom_border_menu_item_click(self, event):
        _, column, row=self._image_text_TextCtrl.PositionToXY(self._image_text_TextCtrl.GetInsertionPoint())

        try:
            if self._math_scanner.place_bottom_border(row, column):
                self._speech.speak("Set")
        except ValueError:
            self._speech.speak("Invalid coordinates")

    def _remove_left_border_menu_item_click(self, event):

        if self._math_scanner.remove_left_border():
            self._speech.speak("Removed")
    def _remove_right_border_menu_item_click(self, event):

        if self._math_scanner.remove_right_border():
            self._speech.speak("Removed")
    def _remove_top_border_menu_item_click(self, event):

        if self._math_scanner.remove_top_border():
            self._speech.speak("Removed")
    def _remove_bottom_border_menu_item_click(self, event):

        if self._math_scanner.remove_bottom_border():
            self._speech.speak("Removed")

    def _recognize_bordered_region_menu_item_click(self, event):
        img=self._math_scanner.get_bordered_region()

        wx.MessageBox(str(self._math_scanner.recognize(img)))
    def _recognize_full_image_menu_item_click(self, event):
        print("click2")

    def _main_window_close(self, event):
        self._speech.release()

        event.Skip()

    # Helper methods

    def _open_image(self, path):
        try:
            self._math_scanner.load_image_from_file(path)
            self._image_text_TextCtrl.SetValue(self._math_scanner.image_text)
            self._set_window_title()
        except:
            print("Error")

app=wx.App(False)
main_window=MainWindow()
main_window.Show(True)
app.MainLoop()

