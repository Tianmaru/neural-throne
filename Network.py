import numpy
from PIL import Image
from PIL import ImageFilter
import tflearn
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.recurrent import lstm
from tflearn.layers.estimator import regression
import os
import TrainingData

from tflearn.data_preprocessing import ImagePreprocessing
# numpy.set_printoptions(threshold=numpy.nan)
LEARNING_RATE = 0.001


def neural_network_model():
    input_x, input_y, output_size = 240, 320, 13
    network = input_data(shape=[None, input_x, input_y, 1], name='input')
    network = conv_2d(network, nb_filter=32, filter_size=5, activation='relu')
    network = max_pool_2d(network, kernel_size=2)
    network = conv_2d(network, nb_filter=64, filter_size=5, activation='relu')
    network = max_pool_2d(network, kernel_size=2)
    network = conv_2d(network, nb_filter=64, filter_size=5, activation='relu')
    network = max_pool_2d(network, kernel_size=2)
    network = fully_connected(network, 512)
    network = dropout(network, 0.8)
    network = fully_connected(network, 512)
    network = dropout(network, 0.8)
    network = fully_connected(network, output_size, activation='sigmoid')
    #  output values between 0 and 1, divide axes in 2 separate values
    network = regression(network, optimizer='adam', loss='categorical_crossentropy', learning_rate=LEARNING_RATE)
    model = tflearn.DNN(network, tensorboard_dir='log')
    return model


def train(X, y, model=None):
    if model is None:
        model = neural_network_model()
    model.fit(X, y, n_epoch=5, validation_set=0.1, show_metric=True, run_id='neural-throne')
    model_path = os.path.abspath(os.path.dirname(__file__)) + "\\" + 'models'
    if not os.path.exists(model_path):
        os.makedirs(model_path)
    model.save(model_path+'\\'+'neural-throne.tfl')


def output2list(output_data):
    axes = output_data['axes']
    buttons = output_data['buttons']
    x_positive = 0 if axes[0] < 0 else axes[0] #  right
    x_negative = 0 if axes[0] > 0 else abs(axes[0]) #  left
    y_positive = 0 if axes[1] < 0 else axes[1] #  down
    y_negative = 0 if axes[1] > 0 else abs(axes[1]) #  up
    lt = 0 if axes[2] < 0 else axes[2] #  skill
    rt = 0 if axes[2] > 0 else abs(axes[2]) #  shoot
    ry_positive = 0 if axes[3] < 0 else axes[3]
    ry_negative = 0 if axes[3] > 0 else abs(axes[3])
    rx_positive = 0 if axes[4] < 0 else axes[4]
    rx_negative = 0 if axes[4] > 0 else abs(axes[4])
    btn_a = float(buttons[0])
    btn_x = float(buttons[2])
    btn_y = float(buttons[3])
    y = [x_positive,x_negative,y_positive,y_negative,lt,rt,rx_positive,rx_negative,ry_positive,ry_negative,
         btn_a,btn_x,btn_y]
    return y


def transform_data(training_data,path=''):
    X, y = [], []
    for sample in training_data:
        image = Image.open(path+sample.input_data['image'])
        # image = image.filter(ImageFilter.FIND_EDGES)
        image = image.convert('L') #  convert to grayscale
        #  shape (240,320)
        X.append(numpy.array(image).reshape([240,320,1])/255)
        y.append(output2list(sample.output_data))
    y = numpy.array(y)
    return X, y


if __name__ == '__main__':
    PATH = 'training-data\\'
    FILE = 'training-data.xml'
    print('Parsing XML...')
    training_data = TrainingData.parse_xml(PATH + FILE)
    print('Found {} samples'.format(len(training_data)))
    print('Loading samples...')
    X, y = transform_data(training_data, PATH)
    print('Loading finished!')
    train(X, y)

