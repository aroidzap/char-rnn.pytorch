# https://github.com/spro/char-rnn.pytorch

import unidecode
import string
import time
import math
import torch

# Reading and un-unicode-encoding data

extra_characters = "äüŤćöĎ”ŇŮÚ‘ÝÉĚŘÁÍŠóÓŽČ’úďň“„ť–ůčéýřšžěáí"
all_characters = string.printable + extra_characters
n_characters = len(all_characters)

def read_file(filename):
    t = time.time()
    contents = ""
    with open(filename, encoding="utf-8") as f:
        file_data = f.read()
        for i, c in enumerate(file_data):
            if time.time() - t > 3:
                print(f"Parsing '{filename}' {100 * i / len(file_data):.1f}%.")
                t = time.time()
            if c in all_characters:
                contents += c
            else:
                contents += unidecode.unidecode(c)
    return contents, len(contents)

# Turning a string into a tensor

def char_tensor(string):
    tensor = torch.zeros(len(string)).long()
    for c in range(len(string)):
        try:
            tensor[c] = all_characters.index(string[c])
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
