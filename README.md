# Math scanner

Reading mathematical expressions in images with screenreaders has been always difficult. Available OCR programs have over time get very good at recognizing ordinary text, but the space notation used by mathematics is still difficult to read for them.

Meanwhile, a promising new service, [Mathpix](https://mathpix.com/) has appeared, offering quick and very accurate deep learning based recognition of not just mathematical expressions and equations, but also other scientific figures such as tables, chemical diagrams and various kinds of formatting. While this seemed like a way to go for screenreaders, there was one major drawback. Mathpix requires a cropped image of the formula or figure to be transcribed, one can't just enter a page and get the desired results.

While this may seem like a clear stopper, Math scanner tries to overcome this issue.

It takes an input image and runs it through Tesseract to get the image text. After this is done, it allows the user to border the badly recognized mathematical notation by marking the characters from text around it. Information about bounding boxes of these characters is then used to crop the formula, which is send to Mathpix for recognition.

The app is currently mostly a proof of concept, but it's already functional and contains few useful functions.

## Getting things ready

### Dependencies

In order to work properly, Math scanner needs some dependencies to be installed.

First of all, install the necessary libraries:\
```pip3 install appdirs pillow pytesseract pyyaml```

You can also try to install WXPython in this way, but at least in my case, despite my effort I was not able to get it to compile properly. Thus I recommend installing one of the [pre-build wheels,](https://wxpython.org/pages/downloads/index.html) if you want to save time and nerves.

The last dependencies you need are Speech dispatcher (on Linux) and Tesseract. If you're running Orca, you probably already have the former and you can get the latter easily from your distribution's repository or from the project's [official repository.](https://github.com/tesseract-ocr/tesseract)

The way you install Tesseract doesn't matter much. It just has to be executable by ```tesseract``` command, so make sure it's installed on a visible place or included in path.

### Setting up Mathpix OCR api

Another thing you need before using Math scanner is a working pair of Mathpix app ID and App key.

To get these, visit the [Mathpix's official page](https://mathpix.com/) and create an account.

After this, login to your account and visit the [OCR page,](https://accounts.mathpix.com/ocr-api) where you can create your API.

Note that Mathpix OCR is a paid service. Although the price is not by any means dramatic, make sure to check out [the pricing](https://mathpix.com/ocr#pricing) to get familiar with the current prices.

After setting up the API, save the App ID and App key. Youll need them in Math scanner configuration.

### Installation and configuration

Math scanner is currently really a single Python script.

On a Linux system, you'll probably want to make it executable:\
```chmod u+x math_scanner.py```

And may be also install it to your bin directory (omitting the extension for convenience):\
```sudo cp math_scanner.py /usr/bin/math_scanner```

Math scanner takes path to a file to recognize as a optional argument, so you can open images in it from your desktop environment without complicated searching.

Both operations are however not necessary and you can use the script also in a portable way.

There is a single configuration file settings.yaml. This file holds the configuration for Math scanner, and the program currently searches for it in user's configuration directory (on Linux ```~/.config/math_scanner``` by default) as well as in the current working directory.

It's a yaml document, holding the configuration in few objects. Try not to mess up the indentation much, as it's important in the parsing process.

Individual options will be described later. Currently, the most important thing you need to set is the app id and app key of the mathpix object.

When this is done, you can start using the application.

## Usage

### Loading an image

The first thing you usually want to do is to load an image to work with. You can do this either wia your desktop environment, through terminal by providing the path to the image as an argument or through the app itself wia the File/Open menu entry (Ctrl+O).

You can use images of practically anything, from formulas found on the web, through screenshots to full pages from a document. It's important to say here though, that Math scanner currently doesn't support PDF files, so if you want to read a PDF document, you'll need to extract the pages first.

After loading the image (recognition can take a while), you should see its text in the text area.

If it's too hard to read, try adjusting the input processing parameters, various operations can improve the readability of the page.

### Borders

In order to border a part of the image, usually containing a formula or an expression, Math scanner introduces the concept of "borders".

You can imagine a border like a stick or a straight ruler, which crosses the image from edge to edge either horizontally or vertically.

You need to place four borders in order to enclose a region - left, right, top and bottom. You can do so using options from the Borders menu, each has its own keyboard shortcut to make the action confortable, as you'll do this quite often.

These borders are being placed as follows:
* The left border is placed to the left from the currently focused character.
* The right border is placed to the right from the currently focused character.
* The top border is placed from the top of the currently focused character.
* The bottom border is placed from the bottom of the currently focused character.

After placing a border, you can move it by placing it again if needed, but only in its name's direction i.e. left border to the left, right border to the right etc. This rule is intended to reflect the fact, that when you have three lines where you know is a formula, you can't determine which character to use for placing the left border as an example, because the text in view is not horizontally formatted. You can instead use the beginning characters of all three lines and this rule will only let you move the border away from the expression, preventing you from cutting it.

You however don't necessarily need to place all 4 borders. If either of the four borders is not placed, the image's edge according to that border's name is used instead.

For example, if you want to border a row of text in a single column document, you only need to place the top and bottom borders. Left and right will be considered to be on edges, including the whole row in the result.

As for placing the top and bottom borders in the preceding example, it's usually not a good idea to do so directly on the target line. Various characters have various sizes and even if you're lucky and don't cut anything, the resulting image is usually tight enough for OCR to do weird things.

Instead, You can place the bottom border on the line above and the top border on the line below. While this may seem counter-intuitive at first, it makes perfect sense. The bottom border is always placed from the bottom of the focused character, so if you place it on the line above, you'll place it below that line and therefore above your target line with some offset. The same goes for placing the top border, just in a reversed way.

When cropping the bordered image, Math scanner switches the borders internally to correspond with their names without touching your placement, so you'll get correct result.

The only exception to this rule is, when one of the borders which are usually switched (left - right or top - bottom) is not set. This is a normal state, as the switch is not necessary. But you sometimes want to do it, for example if you want to select everything below the last line of the image.

In this case, you can place the bottom border on the last line and force the switch using the Borders/Switch horizontal borders menu entry. Note that the name refers to horizontal borders, not horizontal switching.

Bordering strategies for formulas and expressions depend on the concrete situation. If you have a single column with a formula taking up a whole line or few, you usually need to place just the top and bbottom border, ideally in the reversed way as described above.

There are however also situations, when a formula is included in text. Then you usually need to place left and right borders as well (the less text in the image, the better results). You can again place them reversed to make a suitable selection.

### Columns

Various materials, usually books, don't necessarily need to be printed in just one column, but can also have two or even more of them. Math scanner currently can't deal with this by itself, but offers you tools to mark the columns and process them individually.

there are two typical situations, where you can clearly see that you're working with a two columns based document:
* Two unrelated sentences are on a single line, they may be even interrupted on the places where the text wraps in their respective column.
* Two unrelated lines are one below another. Usually Each odd line may be part of one text, while each even line is clearly a part of another, or some similar model with occasional interuptions by graphics and similar elements.

If you see a situation like this, you can split the columns easily. Find a place, where the text of the first column wraps, the - sign used to mark this can be useful here. When you find it, place the right border on the last non-space character of the column.\
Then find a place, where the second column begins horizontally. Looking for a beginning of related sentence may be a good idea, but if you have the second mentioned scenario with lines one below another, you can also pick up one and use its' starting character. When you find it, place the left border there.

Now, as both borders are placed, activate the Columns/Split to columns menu entry. Internally, the program will:
* Switch the borders if needed, so they represent their names
* calculate a virtual vertical line crossing the selected region in the middle, splitting the columns
* Split the image across the calculated line and run each column through Tesseract for text recognition
* Switch to column view (if not active already), and remove any borders placed by the user before the process as they're not relevant anymore

In the column view, you can switch individual columns with Alt+Left & Alt+Right shortcuts and work with them separately. Each switch will remove any borders you've placed on the column.

The information about the currently active column will be displayed in the title of the window.

If there are more columns to split, you can do so in the same way as before.

If you decide, that you want to return to the original image, you can cancel the columns from the Columns menu.

### Math recognition

When you have your expression bordered, you can navigate to the Recognition menu and select the Recognize option. All menus are accessible with Alt+First letter shortcuts and because this item is first in its menu, you can simply press Alt+R followed by the return key to activate the recognition.

The program will display a MessageBox with the result in the configured format. You can also view the full json response from here if you want.

## Configuration

This section describes each object in the Math scanner configuration, its role and possible values.

### mathpix

Configures various parameters related to the Mathpix service.

Parameter | Description | Value | Default
--- | --- | --- | ---
app id | Your Mathpix App ID | String | your_app_id
app key | Your Mathpix App Key | String | your_app_key
formats | Formats of expressions returned by Mathpix | An array of string values asciimath or latex simplified | [asciimath, latex simplified]

### Tesseract

Stores parameters for Tesseract OCR engine.

Parameter | Description | Value | Default
--- | --- | --- | ---
data directory | The path to the directory containing Tesseract models and scripts | Path or default keyword, leaving the selection to Tesseract | default
recognition language | The language(s) of the OCr | Three letter codes such as eng, slk or deu, concatenated by + sign if the document contains multiple languages | eng
ocr engine mode | Decides, if the recognition should use Legacy, Neural networks based LSTM or both models | 0 - Legacy only, 1 - LSTM only, 2 - Legacy + LSTM, 3 - Tesseract default, based on what models are available | 3

### input / output image processing

Both sections (input image processing and output image processing) configure various image operations performed on the passing images.

Input image is the image you load to Math scanner, its processing is done before passing it to Tesseract. Output image is the cropped image sent to Mathpix, the processing is done before sending.

Both configurations share the same options, so Im merging them together here.

When implementing the image processing operations, I got inspiration from the great [OCRDesktop project.](https://github.com/chrys87/ocrdesktop) I definitely recommend checking it out, if you're on Linux.

Parameter | Description | Value | Default
--- | --- | --- | ---
scale factor | Scales the image by the given factor | Real number | 1
invert | Inverts colours | Boolean (yes or no) | no
grayscale | Converts the image to grayscale | Boolean (yes or no) | no
blackwhite | Everything under a given threshold is casted to black, the rest to white | Boolean (yes or no) | no
blackwhite threshold | The threshold for blackwhite function | Number from 0 to 255 including | 200

### speech

Configures the speech parameters. The speech system used on Linux is Speech dispatcher.

Parameter | Description | Value | Default
--- | --- | --- | ---
speech module | The speech module to use | The module's name | espeak-ng
language | The language of the speech | Depends on the speech module, but usually two letter code like en, sk or de | en
voice | Name of the voice to be used | String | male1
punctuation mode | Defines the level of pronouncing punctuation by the speech module | none, some or all | some
pitch | The pitch of the speech | Number from -100 to 100 | 10
rate | The rate of the speech | Number from -100 to 100 | 2
volume | The volume of the speech | Number from -100 to 100 | 100

## Final notes

### Limitations

As stated on the beginning, this app is for now mostly a proof of concept. While its core functionality technically works, there are few limitations to keep in mind:
* No support for PDF. If the app proves itself to be useful and it will be known on what kinds of documents it works the best, this will be considered, but for now, more testing is necessary.
* Problems with rotation. Tesseract seems to be bit troublesome, when it comes to getting bounding boxes of individual characters. They can be optained, but with the drawback of losing the information about their position in word, line, block etc. I wrote my own algorithm to assign them to places and it seems to work, whith one exception. If the text is even slightly rotated, you're done.
* Sometimes you may encounter that spaces are missing in the text. This is again a mistake of my algorithm, which has predefined size of a space to 10 pixels, whatever that means. I wanted to make it dynamic, but then I decided to wait a bit, as not placing spaces seems to be an interesting indicator that the recognized text was too small on the image and something might be missing. More tests are required to see whether this is true and to what extend.

### Platforms

Currently, Math scanner is primarily for Linux. However, the code is written in a mostly crossplatform way and it technically could be used on other platforms as well with minimal changes.

If you want to do so, you have two options:
* Provide a speech class for your platform, following the methods of LinuxSpeech class. Then comment out the speechd import and in MainWindow, replace LinuxSpeech initialization of self._speech with your class.
* Comment out the speechd import as well as everything with self._speech. This way you will lose the speech, but the program should work, so it's upto you how important is it.

