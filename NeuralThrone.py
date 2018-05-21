from PIL import Image
import numpy
import time
import keyboard
from TrainingData import beep
from Screenshot import getScreenShot
from Network import neural_network_model
import pyxinput
#numpy.set_printoptions(threshold=numpy.nan) #requires from numpy import *

def process_image(image):
    width, height = image.size
    roi = (240, 0, 1680, height)
    image = image.crop(roi)
    image = image.resize((320, 240))
    image = image.convert('L')
    input_data = numpy.array(image)/255
    input_data = input_data.reshape((240, 320, 1))
    return input_data


# canny edge detection
# processed_image = cv2.Canny(processed_image, threshold1=50, threshold2=300)

def update_controller(virtual_controller, output_data):
    x_positive = output_data[0]
    x_negative = output_data[1]
    y_positive = output_data[2]
    y_negative = output_data[3]
    lt = output_data[4]
    rt = output_data[5]
    ry_positive = output_data[6]
    ry_negative = output_data[7]
    rx_positive = output_data[8]
    rx_negative = output_data[9]
    btn_a = round(output_data[10])
    btn_x = round(output_data[11])
    btn_y = round(output_data[12])
    virtual_controller.set_value('AxisLx', x_positive-x_negative)
    virtual_controller.set_value('AxisLy', y_negative - y_positive)
    virtual_controller.set_value('TriggerL', lt)
    virtual_controller.set_value('TriggerR', rt)
    virtual_controller.set_value('AxisRx', rx_positive - rx_negative)
    virtual_controller.set_value('AxisRy', ry_negative - ry_positive)
    virtual_controller.set_value('BtnA', btn_a)
    virtual_controller.set_value('BtnX', btn_x)
    virtual_controller.set_value('BtnY', btn_y)

if __name__ == '__main__':
    print('Loading model...')
    PATH = 'models\\'
    FILE = 'neural-throne.tfl'
    model = neural_network_model()
    model.load(PATH+FILE)
    AUTO_KEY = 'F5'
    USER_KEY = 'F6'
    STOP_KEY = 'F9'
    WINDOW_NAME = 'Nuclear Throne'
    virtual_controller = pyxinput.vController()
    usermode = True;
    running = True
    while running:
        if usermode:
            virtual_controller.set_value('BtnA', keyboard.is_pressed('enter'))
            virtual_controller.set_value('BtnB', keyboard.is_pressed('escape'))
            virtual_controller.set_value('AxisLx', keyboard.is_pressed('right') - keyboard.is_pressed('left'))
            virtual_controller.set_value('AxisLy', keyboard.is_pressed('up') - keyboard.is_pressed('down'))
        else:
            result, screen = getScreenShot(WINDOW_NAME)
            if result:
                input_data = [process_image(screen)]
                output_data = model.predict(input_data)[0]
                print(output_data)
                update_controller(virtual_controller, output_data)
        if keyboard.is_pressed(USER_KEY) and not usermode:
            usermode = True
            print('Mode: User')
        elif keyboard.is_pressed(AUTO_KEY) and usermode:
            usermode = False
            print('Mode: Auto')
        if keyboard.is_pressed(STOP_KEY):
            running = False
    beep()