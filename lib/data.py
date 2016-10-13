'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
'''Simple data loader module.

Loads data files from the "data" directory shipped with a game.

Enhancing this to handle caching etc. is left as an exercise for the reader.
'''

import os
from os.path import join as join_path

data_py = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.normpath(join_path(data_py, '..', 'data'))
path = dict(
    font  = join_path(data_dir, 'font'),
    image = join_path(data_dir, 'image'),
    map   = join_path(data_dir, 'map'),
    sound = join_path(data_dir, 'sound'),
    text  = join_path(data_dir, 'text'),
)

def filepath(typ, filename):
    '''Determine the path to a file in the data directory.
    '''
    return join_path(path[typ], filename)

def load(typ, filename, mode='rb'):
    '''Open a file in the data directory.

    "mode" is passed as the second arg to open().
    '''
    return open(filepath(typ, filename), mode)

def load_font(filename):
    return load('font', filename)

def load_image(filename):
    return load('image', filename)

def load_map(filename):
    return load('map', filename)

def load_sound(filename):
    return load('sound', filename)

def load_text(filename):
    return load('text', filename, 'r')
