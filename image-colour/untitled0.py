#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 17:24:56 2018

@author: divyanshu
"""
import numpy as np
import PIL

image = Image.open('test.jpeg')
w, h = image.size
lol = image.getcolors(w*h)
a = np.array((120, 124, 130))
b = np.array((0,0,0))

dist = np.linalg.norm(a-b)