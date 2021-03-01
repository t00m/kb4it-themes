#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Log module.

# File: utils.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: log module
"""

import os
import sys
import subprocess


def which(program):
    """
    Missing method docstring (missing-docstring)
    """
    if sys.platform == 'win32':
        program = program + '.exe'

    def is_exe(fpath):
        """
        Missing method docstring (missing-docstring)
        """
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def execmd(cmd):
    process = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = process.communicate()
    return (output, errors)
