#!/usr/bin/env python
# ./mkimage.sh --tag m1 m1.py
from __future__ import absolute_import, division, print_function

import os
import shutil
import subprocess
import sys

files=[
    '/usr/bin/bash',
    '/usr/bin/ls',
]
os.chdir(sys.argv[1])
os.umask(0o22)

for d in (
    'etc',
    'tmp',
    'var/tmp',
    'usr/bin',
    'usr/lib',
    'usr/lib64',
    'usr/sbin',
):
    os.makedirs(d, mode=0o777)

for s in ('bin', 'lib', 'lib64', 'sbin'):
    os.symlink('usr/' + s, s)

def _copy(fn):
    shutil.copy2(fn, fn.lstrip('/'))
    return fn

libs=set()
for p in files:
    _copy(p)
    try:
        for l in subprocess.check_output(['ldd', p]).split():
            if l.startswith('/'):
                libs.add(l)
    except Exception as e:
        print(e)

for l in libs:
    _copy(l)
