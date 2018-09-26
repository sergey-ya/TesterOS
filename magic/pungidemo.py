#!/usr/bin/python
# coding: utf_8


import time, os
import sys


sys.stdout.write('строка1\n')
sys.stdout.flush()
time.sleep(5)
sys.stdout.write('строка2\n')
sys.stdout.flush()
time.sleep(5)
sys.stdout.write('строка3\n')
sys.stdout.flush()
time.sleep(50)
sys.stdout.write('строка4\n')
sys.stdout.flush()
time.sleep(50)
sys.stdout.write('строка5\n')
sys.stdout.flush()
time.sleep(50)
sys.stdout.write('end')

