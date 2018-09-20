# -*- coding: utf-8 -*-
"""
Class definition of YOLO_v3 style detection model on image and video
"""

#!/usr/bin/python

import colorsys
import os
from timeit import default_timer as timer

import collections

from subprocess import call

import cv2
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from PIL import Image

import numpy as np
from keras import backend as K
from keras.models import load_model
from keras.layers import Input
from PIL import Image, ImageFont, ImageDraw

from yolo3.model import yolo_eval, yolo_body, tiny_yolo_body
from yolo3.utils import letterbox_image
from keras.utils import multi_gpu_model

class YOLO(object):
    _defaults = {
        "model_path": '/home/divyanshu/Desktop/YOLO/model_data/yolo.h5',
        "anchors_path": '/home/divyanshu/Desktop/YOLO/model_data/yolo_anchors.txt',
        "classes_path": '/home/divyanshu/Desktop/YOLO/model_data/coco_classes.txt',
        "score" : 0.3,
        "iou" : 0.45,
        "file_path" : '/home/divyanshu/Desktop/YOLO/output/objectList.txt',
        "model_image_size" : (416, 416),
        "gpu_num" : 1,
    }
    
    c = 1

    @classmethod
    def get_defaults(cls, n):
        if n in cls._defaults:
            return cls._defaults[n]
        else:
            return "Unrecognized attribute name '" + n + "'"

    def __init__(self, **kwargs):
        self.__dict__.update(self._defaults) # set up default values
        self.__dict__.update(kwargs) # and update with user overrides
        self.class_names = self._get_class()
        self.anchors = self._get_anchors()
        self.sess = K.get_session()
        self.boxes, self.scores, self.classes = self.generate()

    def _get_class(self):
        classes_path = os.path.expanduser(self.classes_path)
        with open(classes_path) as f:
            class_names = f.readlines()
        class_names = [c.strip() for c in class_names]
        return class_names

    def _get_anchors(self):
        anchors_path = os.path.expanduser(self.anchors_path)
        with open(anchors_path) as f:
            anchors = f.readline()
        anchors = [float(x) for x in anchors.split(',')]
        return np.array(anchors).reshape(-1, 2)

    def generate(self):
        model_path = os.path.expanduser(self.model_path)
        assert model_path.endswith('.h5'), 'Keras model or weights must be a .h5 file.'

        # Load model, or construct model and load weights.
        num_anchors = len(self.anchors)
        num_classes = len(self.class_names)
        is_tiny_version = num_anchors==6 # default setting
        try:
            self.yolo_model = load_model(model_path, compile=False)
        except:
            self.yolo_model = tiny_yolo_body(Input(shape=(None,None,3)), num_anchors//2, num_classes) \
                if is_tiny_version else yolo_body(Input(shape=(None,None,3)), num_anchors//3, num_classes)
            self.yolo_model.load_weights(self.model_path) # make sure model, anchors and classes match
        else:
            assert self.yolo_model.layers[-1].output_shape[-1] == \
                num_anchors/len(self.yolo_model.output) * (num_classes + 5), \
                'Mismatch between model and given anchor and class sizes'

        print('{} model, anchors, and classes loaded.'.format(model_path))

        # Generate colors for drawing bounding boxes.
        hsv_tuples = [(x / len(self.class_names), 1., 1.)
                      for x in range(len(self.class_names))]
        self.colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
        self.colors = list(
            map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)),
                self.colors))
        np.random.seed(10101)  # Fixed seed for consistent colors across runs.
        np.random.shuffle(self.colors)  # Shuffle colors to decorrelate adjacent classes.
        np.random.seed(None)  # Reset seed to default.

        # Generate output tensor targets for filtered bounding boxes.
        self.input_image_shape = K.placeholder(shape=(2, ))
        if self.gpu_num>=2:
            self.yolo_model = multi_gpu_model(self.yolo_model, gpus=self.gpu_num)
        boxes, scores, classes = yolo_eval(self.yolo_model.output, self.anchors,
                len(self.class_names), self.input_image_shape,
                score_threshold=self.score, iou_threshold=self.iou)
        return boxes, scores, classes
    
    def write_file(self, key, value, file_path):
        with open(file_path, "a") as f:
            f.writelines('"'+str(key)+'":"'+str(value)+'"')

    # K NEAREST NEIGHBOURS HISTOGRAM

    def find_histogram(clt):
        """
        create a histogram with k clusters
        :param: clt
        :return:hist
        """
        numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
        (hist, _) = np.histogram(clt.labels_, bins=numLabels)

        hist = hist.astype("float")
        hist /= hist.sum()

        return hist

    def plot_colors2(hist, centroids):
        bar = np.zeros((50, 300, 3), dtype="uint8")
        startX = 0

        for (percent, color) in zip(hist, centroids):
            # plot the relative percentage of each cluster
            endX = startX + (percent * 300)
            cv2.rectangle(bar, (int(startX), 0), (int(endX), 50),
                        color.astype("uint8").tolist(), -1)
            startX = endX

        # return the bar chart
        return bar

    def get_pixel(image, i, j):
        # Inside image bounds?
        width, height = image.size
        if i > width or j > height:
            return None

        # Get Pixel
        pixel = image.getpixel((i, j))
        return pixel
    
    def convert_primary(image):
        # Get size
        width, height = image.size

        # Create new Image and a Pixel Map
        new = Image.new("RGB", (width, height), "white")
        pixels = new.load()

        # Transform to primary
        for i in range(width):
            for j in range(height):
                # Get Pixel
                pixel = YOLO.get_pixel(image, i, j)

                # Get R, G, B values (This are int from 0 to 255)
                red =   pixel[0]
                green = pixel[1]
                blue =  pixel[2]

                # Transform to primary
                if red > 127:
                    red = 255
                else:
                    red = 0
                if green > 127:
                    green = 255
                else:
                    green = 0
                if blue > 127:
                    blue = 255
                else:
                    blue = 0

                # Set Pixel in new image
                pixels[i, j] = (int(red), int(green), int(blue))

            # Return new image
        return new
    
    def detect_image(self, image, file_path):
        start = timer()

        if self.model_image_size != (None, None):
            assert self.model_image_size[0]%32 == 0, 'Multiples of 32 required'
            assert self.model_image_size[1]%32 == 0, 'Multiples of 32 required'
            boxed_image = letterbox_image(image, tuple(reversed(self.model_image_size)))
        else:
            new_image_size = (image.width - (image.width % 32),
                              image.height - (image.height % 32))
            boxed_image = letterbox_image(image, new_image_size)
        image_data = np.array(boxed_image, dtype='float32')

        print(image_data.shape)
        image_data /= 255.
        image_data = np.expand_dims(image_data, 0)  # Add batch dimension.

        out_boxes, out_scores, out_classes = self.sess.run(
            [self.boxes, self.scores, self.classes],
            feed_dict={
                self.yolo_model.input: image_data,
                self.input_image_shape: [image.size[1], image.size[0]],
                K.learning_phase(): 0
            })
                    
        print('\nFound {} boxes for {}\n'.format(len(out_boxes), 'img'))

        font = ImageFont.truetype(font='/home/divyanshu/Desktop/YOLO/font/FiraMono-Medium.otf',
                    size=np.floor(3e-2 * image.size[1] + 0.5).astype('int32'))
        thickness = (image.size[0] + image.size[1]) // 300
        
        classArray = collections.Counter(list(out_classes))
        
        if list(classArray.keys()):
            with open(file_path, "a") as f:
                f.write('{')
            self.write_file(self.class_names[list(classArray.keys())[0]], list(classArray.values())[0], file_path)
            for i in range(1, len(list(classArray.keys()))):
                with open(file_path, "a") as f:
                    f.write(',')
                self.write_file(self.class_names[list(classArray.keys())[i]], list(classArray.values())[i], file_path)
            with open(file_path, "a") as f:
                f.write('},\n')
        
        for i, c in reversed(list(enumerate(out_classes))):
            predicted_class = self.class_names[c]
            box = out_boxes[i]
            score = out_scores[i]

            top, left, bottom, right = box
            top = max(0, np.floor(top + 0.5).astype('int32'))
            left = max(0, np.floor(left + 0.5).astype('int32'))
            bottom = min(image.size[1], np.floor(bottom + 0.5).astype('int32'))
            right = min(image.size[0], np.floor(right + 0.5).astype('int32'))
            car_color = ''
            if predicted_class == 'car' and score > 0.50:
                crop_img = image.crop((int(left),int(top),int(right),int(bottom)))
                w, h = crop_img.size
                primary_image = YOLO.convert_primary(crop_img)
                pixels = primary_image.getcolors(w * h)
                most_frequent_pixel = (0, (14, 0, 0))
                for count, colour in pixels:
                    if colour != (255, 0, 255) and colour != (255, 255, 255) and colour != (0, 0, 0):
                        if count > most_frequent_pixel[0]:
                            most_frequent_pixel = (count, colour)
                
                if most_frequent_pixel[1] == (0, 0, 255):
                    car_color = 'red'
                elif most_frequent_pixel[1] == (0, 255, 0):
                    car_color = 'green'
                elif most_frequent_pixel[1] == (255, 0, 0):
                    car_color = 'blue'
                elif most_frequent_pixel[1] == (255, 255, 0):
                    car_color = 'yellow'
                elif most_frequent_pixel[1] == (0, 255, 255):
                    car_color = 'light blue'
                elif most_frequent_pixel[1] == (255, 0, 255):
                    car_color = 'pink'          
                # crop_img.show()
                # primary_image.show()
                # plt.imshow([[most_frequent_pixel[1]]])
                # plt.show()
                
                # print("Most Common", most_frequent_pixel[1])

                # img = np.asarray(crop_img)
                # # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                # img = img.reshape((img.shape[0] * img.shape[1],3)) #represent as row*column,channel number
                # clt = KMeans(n_clusters=3) #cluster number
                # clt.fit(img)

                # hist = YOLO.find_histogram(clt)
                # bar = YOLO.plot_colors2(hist, clt.cluster_centers_)

                # plt.axis("off")
                # # plt.imshow(bar)
                # # plt.savefig('foo.png', bbox_inches='tight')
                # plt.show()

            label = '{} {:.2f}'.format(predicted_class, score)
            draw = ImageDraw.Draw(image)
            label_size = draw.textsize(label, font)

            print(label, (left, top), (right, bottom)) # Bounding box out

            if top - label_size[1] >= 0:
                text_origin = np.array([left, top - label_size[1]])
            else:
                text_origin = np.array([left, top + 1])

            # My kingdom for a good redistributable image drawing library.
            for i in range(thickness):
                draw.rectangle(
                    [left + i, top + i, right - i, bottom - i],
                    outline=self.colors[c])
            draw.rectangle(
                [tuple(text_origin), tuple(text_origin + label_size)],
                fill=self.colors[c])
            if predicted_class == 'car':
                draw.text(text_origin, car_color + ' car', fill=(0, 0, 0), font=font)
            else:
                draw.text(text_origin, label, fill=(0, 0, 0), font=font)
            del draw

        end = timer()
        print(end - start)
        return image

    def close_session(self):
        self.sess.close()

def detect_video(yolo, video_path, output_path, file_path):
    import cv2
    print(video_path)
    print(output_path)
    if video_path == './path2your_video':
        vid = cv2.VideoCapture(0)
    else:
        vid = cv2.VideoCapture(video_path)        
    if not vid.isOpened():
        raise IOError("Couldn't open webcam or video")
    
    video_FourCC    = cv2.VideoWriter_fourcc(*'MJPG')
    
    if video_path == './path2your_video':
        video_fps = 60
    else:
        video_fps = vid.get(cv2.CAP_PROP_FPS)

    video_size      = (int(vid.get(cv2.CAP_PROP_FRAME_WIDTH)),
                        int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    isOutput = True if output_path != "" else False
    if isOutput:
        print("!!! TYPE:", type(output_path), type(video_FourCC), type(video_fps), type(video_size))
        out = cv2.VideoWriter(output_path, video_FourCC, video_fps, video_size)
    accum_time = 0
    curr_fps = 0
    count = 1
    fps = "FPS: ??"
    prev_time = timer()
    with open(file_path, "a+") as f:
        f.write('"'+video_path+'":[\n')
    while True:
        return_value, frame = vid.read()
        if not return_value:
            break
        if count == 1:
            count += 1
            image = Image.fromarray(frame)
            image = yolo.detect_image(image, file_path)
            result = np.asarray(image)
            curr_time = timer()
            exec_time = curr_time - prev_time
            prev_time = curr_time
            accum_time = accum_time + exec_time
            curr_fps = curr_fps + 1
            if accum_time > 1:
                accum_time = accum_time - 1
                fps = "FPS: " + str(curr_fps)
                curr_fps = 0
            cv2.putText(result, text=fps, org=(3, 15), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.50, color=(255, 0, 0), thickness=2)
            cv2.namedWindow("result", cv2.WINDOW_NORMAL)
            cv2.imshow("result", result)
            if isOutput:
                out.write(result)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        elif count < 5:
            image = Image.fromarray(frame)
            count += 1
        elif count == 5:
            image = Image.fromarray(frame)
            count = 1
    with open(file_path, "a+") as f:
        f.write(']')
    yolo.close_session()
    # Note that you have to specify path to script
    call(["node", "node_service/complete.js"]) 