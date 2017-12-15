#!/usr/bin/env python

from __future__ import print_function

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
        print(f + ' -> ' + n)

