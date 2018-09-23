#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 19:25:17 2018

@author: divyanshu
"""
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import cv2

lola = cv2.imread('images.jpeg')    
image = Image.open('images.jpeg')
opencv = np.asarray(image)
opencv = cv2.cvtColor(opencv, cv2.COLOR_BGR2RGB)


w, h = image.size
image = image.resize((w/5, h/5), Image.ANTIALIAS)
pixels = image.getcolors(w * h)

most_frequent_pixel = pixels[0]

for count, colour in pixels:
    if count > most_frequent_pixel[0]:
        most_frequent_pixel = (count, colour)
        
plt.imshow([[most_frequent_pixel[1]]])

print("Most Common", image, most_frequent_pixel[1])