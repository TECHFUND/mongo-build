#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pickle


saved_images = {}
with open("ami-images.pickle","rb") as f:
    saved_images = pickle.load(f)

print saved_images[sys.argv[1]]
