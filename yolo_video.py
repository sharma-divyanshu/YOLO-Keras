import sys
import argparse
from yolo import YOLO, detect_video
from PIL import Image
import time
from subprocess import call
import os

processed_directory = '/vigilandsrecordings/recordings/P-'

def detect_img(yolo):
    while True:
        img = input('Input image filename:')
        try:
            image = Image.open(img)
        except:
            print('Open Error! Try again!')
            continue
        else:
            r_image = yolo.detect_image(image, 'output/lol.txt')
            r_image.show()
    yolo.close_session()

FLAGS = None

if __name__ == '__main__':
    # class YOLO defines the default value, so suppress any default here
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    '''
    Command line options
    '''
    parser.add_argument(
        '--model', type=str,
        help='path to model weight file, default ' + YOLO.get_defaults("model_path")
    )

    parser.add_argument(
        '--anchors', type=str,
        help='path to anchor definitions, default ' + YOLO.get_defaults("anchors_path")
    )

    parser.add_argument(
        '--classes', type=str,
        help='path to class definitions, default ' + YOLO.get_defaults("classes_path")
    )
    
    parser.add_argument(
        '--file_path', type=str,
        help='path to list of detected objects, default ' + YOLO.get_defaults("file_path")
    )

    parser.add_argument(
        '--gpu_num', type=int,
        help='Number of GPU to use, default ' + str(YOLO.get_defaults("gpu_num"))
    )

    parser.add_argument(
        '--image', default=False, action="store_true",
        help='Image detection mode, will ignore all positional arguments'
    )
    '''
    Command line positional arguments -- for video detection mode
    '''
    parser.add_argument(
        "--input", nargs='?', type=str,required=False,default='./path2your_video',
        help = "Video input path"
    )

    parser.add_argument(
        "--output", nargs='?', type=str, default="",
        help = "[Optional] Video output path"
    )

    FLAGS = parser.parse_args()

    if FLAGS.image:
        """
        Image detection mode, disregard any remaining command line arguments
        """
        print("Image detection mode")
        if "input" in FLAGS:
            print(" Ignoring remaining command line arguments: " + FLAGS.input + "," + FLAGS.output)
        detect_img(YOLO(**vars(FLAGS)))

    elif "input" in FLAGS:
        status = detect_video(YOLO(**vars(FLAGS)), FLAGS.input, FLAGS.output, FLAGS.file_path)
        print(status)
        exists = os.path.isfile(processed_directory+str(os.path.splitext(os.path.basename(FLAGS.output))[0])+'.ts')
        if exists:
            print("File already exists. Deleting.")
            os.remove(processed_directory+str(os.path.splitext(os.path.basename(FLAGS.output))[0])+'.ts')
        os.system('sudo ffmpeg -i '+str(FLAGS.output)+' -vcodec libx264 '+os.path.dirname(FLAGS.input)+'/P-'+str(os.path.splitext(os.path.basename(FLAGS.output))[0])+'.ts')
        print("File Converted")
        os.system('sudo rm -f '+str(FLAGS.output))
        print(FLAGS.output+' deleted')
    else:
        print("Must specify at least video_input_path.  See usage with --help.")
