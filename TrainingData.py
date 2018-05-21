from PIL import Image
import numpy
import time
import os
import keyboard
import winsound
import pygame
from Screenshot import getScreenShot
from datetime import datetime
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


class sample:
    def __init__(self, input_data, output_data):
        self.input_data = input_data
        self.output_data = output_data


def parse_xml(source):
    training_data = []
    input_data = {}
    axes = {}
    buttons = {}
    for event, elem in ET.iterparse(source):
        if event == 'end':
            if elem.tag == 'image':
                input_data['image'] = elem.text
            elif elem.tag == 'axis':
                axes[int(elem.attrib['id'])] = float(elem.text)
            elif elem.tag == 'button':
                buttons[int(elem.attrib['id'])] = int(elem.text)
            elif elem.tag == 'sample':
                output_data = {'axes': axes, 'buttons': buttons}
                training_data.append(sample(input_data, output_data))
                input_data = {}
                axes = {}
                buttons = {}
        elem.clear()
    return training_data


def beep():
    frequency = 440  # Set Frequency to A1
    duration = 1000  # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)


def get_output(gamepad, deadzone=0.1):
    '''Returns the user actions for the specified pygame gamepad as ElementTree element.
    The deadzone can be used to replace small axes values with 0.'''
    output = ET.Element('output')
    axes = ET.SubElement(output, 'axes')
    buttons = ET.SubElement(output, 'buttons')
    for i in range(gamepad.get_numaxes()):
        axis = 0 if abs(gamepad.get_axis(i)) < deadzone else gamepad.get_axis(i)
        ET.SubElement(axes, 'axis', attrib={'id': str(i)}).text = str(axis)
    for i in range(gamepad.get_numbuttons()):
        button = gamepad.get_button(i)
        ET.SubElement(buttons, 'button', attrib={'id': str(i)}).text = str(button)
    return output


if __name__ == '__main__':
    pygame.init()
    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    print([x.get_name() for x in joysticks])
    if len(joysticks) > 1:
        gamepad = joysticks[int(input('SELECT JOYSTICK: '))]
    elif len(joysticks) < 1:
        raise Exception('No gamepads found!')
    else:
        gamepad = joysticks[0]
    gamepad.init()
    WINDOW_NAME = 'Nuclear Throne'
    RESIZE = True
    FRAME_CAP = 30
    DIR = "training-data"
    PATH = os.path.abspath(os.path.dirname(__file__)) + "\\" + DIR
    print("Path: %s" % PATH)
    if not os.path.exists(PATH):
        os.makedirs(PATH)
    FILENAME_IMAGE = ""
    FILENAME_DATA = "training-data.xml"
    # data = open(PATH + "\\" + FILENAME_DATA, "a")
    training_data = ET.Element('training-data')
    START_KEY = 'F5'
    STOP_KEY = 'F9'
    print('Press %s to start sampling...' % START_KEY)
    keyboard.wait(START_KEY)
    beep()  # play beep sound to indicate start
    print('Sampling!')
    sampling = True
    while sampling:
        start_time = time.time()
        pygame.event.pump()  # process pygame events
        if not FILENAME_IMAGE == "":
            image.save(PATH + "\\" + FILENAME_IMAGE)
            sample = ET.SubElement(training_data, 'sample')
            ET.SubElement(ET.SubElement(sample, 'input'), 'image').text = FILENAME_IMAGE
            sample.append(get_output(gamepad))
        # get new image
        result, screen = getScreenShot(WINDOW_NAME)
        if result:
            screen = numpy.array(screen)
            if RESIZE:
                # Assume Resolution 1920x1080
                # Extract Region of Interest (Remove Side Art)
                screen = screen[:, 240:1680, :]
            image = Image.fromarray(screen)
            if RESIZE:
                # Resize to smaller Resolution
                image = image.resize((320, 240))
            FILENAME_IMAGE = datetime.now().strftime("%y%m%d-%H%M%S-%f") + ".png"
        else:
            sampling = False
        # Cap Frames
        end_time = time.time()
        sample_time = end_time - start_time
        if sample_time < 1/FRAME_CAP:
            time.sleep(1/FRAME_CAP - sample_time)
        if keyboard.is_pressed(STOP_KEY):
            sampling = False
    tree = ET.ElementTree(training_data)
    tree.write(PATH + "\\" + FILENAME_DATA)
    pygame.joystick.quit()
    pygame.quit()
    beep()

