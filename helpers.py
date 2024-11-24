# https://github.com/spro/char-rnn.pytorch

import unidecode
import string
import time
import math
import torch

# Reading and un-unicode-encoding data

only_lower_characters = True
extra_characters = "äüŤćöĎ”ŇŮÚ‘ÝÉĚŘÁÍŠóÓŽČ’úďň“„ť–ůčéýřšžěáí"
ALL_CHARACTERS = string.printable + extra_characters
if only_lower_characters:
    ALL_CHARACTERS = ''.join(set(ALL_CHARACTERS.lower()))

def process_character(c):
    if only_lower_characters:
        if c.lower() in ALL_CHARACTERS:
            return c.lower()
        else:
            return unidecode.unidecode(c).lower()
    else:
        if c in ALL_CHARACTERS:
            return c
        else:
            return unidecode.unidecode(c)

def read_file(filename):
    t = time.time()
    contents = ""
    with open(filename, encoding="utf-8") as f:
        file_data = f.read()
        for i, c in enumerate(file_data):
            if time.time() - t > 3:
                print(f"Parsing '{filename}' {100 * i / len(file_data):.1f}%.")
                t = time.time()
            contents += process_character(c)
    return contents, len(contents)

# Turning a string into a tensor

def char_tensor(string):
    tensor = torch.zeros(len(string)).long()
    for c in range(len(string)):
        try:
            tensor[c] = ALL_CHARACTERS.index(string[c])
        except:
            continue
    return tensor

# Readable time elapsed

def time_since(since):
    s = time.time() - since
    m = math.floor(s / 60)
    s -= m * 60
    return '%dm %ds' % (m, s)

def set_torch_device(override=None, verbose=False):
    if override is None:
        if torch.cuda.is_available():
            device = torch.device('cuda')
            if verbose:
                print(f"Using GPU: {torch.cuda.get_device_name(0)}")
        elif torch.backends.mps.is_available():
            device = torch.device('mps')
            if verbose:
                print(f"Using MPS: {torch.backends.mps.is_available()}")
        else:
            device = torch.device('cpu')
            if verbose:
                print(f"Using CPU: {torch.device('cpu')}")
    else:
        device = torch.device(override)
    return device
