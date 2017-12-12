#!/usr/bin/env python

import os
import sys

for f in os.listdir('.'):
    l = f.split('.')
    l[-1] = l[-1].upper()
    n = '.'.join(l)
    if f != n:
        if os.path.isdir(f):
            continue

        os.rename(f, n)
        print f, '->', n

