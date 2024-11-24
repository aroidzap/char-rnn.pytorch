#!/usr/bin/env python
# https://github.com/spro/char-rnn.pytorch

import torch
import os
import argparse

from helpers import *
from model import *

def generate(char_rnn, device, prime_str='\n', predict_len=500, temperature=0.8):

    prime_str = ''.join([process_character(c) for c in prime_str])

    hidden = char_rnn.init_hidden(1)
    prime_input = Variable(char_tensor(prime_str).unsqueeze(0))

    hidden = hidden.to(device)
    prime_input = prime_input.to(device)
    predicted = prime_str

    # Use priming string to "build up" hidden state
    for p in range(len(prime_str) - 1):
        _, hidden = char_rnn(prime_input[:,p], hidden)
        
    inp = prime_input[:,-1]
    
    for p in range(predict_len):
        output, hidden = char_rnn(inp, hidden)
        
        # Sample from the network as a multinomial distribution
        output_dist = output.data.view(-1).div(temperature).exp()
        top_i = torch.multinomial(output_dist, 1)[0]

        # Add predicted character to string and use as next input
        predicted_char = ALL_CHARACTERS[top_i]
        predicted += predicted_char
        inp = Variable(char_tensor(predicted_char).unsqueeze(0))
        inp = inp.to(device)

    return predicted

# Run as standalone script
if __name__ == '__main__':

    # Parse command line arguments
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-m', '--model', type=str, default="model/model.pt")
    argparser.add_argument('-p', '--prime_str', type=str, default='\n')
    argparser.add_argument('-l', '--predict_len', type=int, default=500)
    argparser.add_argument('-t', '--temperature', type=float, default=0.8)
    argparser.add_argument('--device', type=str, default=None) # cpu, cuda, mps
    args = argparser.parse_args()

    device = set_torch_device(args.device)

    char_rnn = CharRNN.load(args.model, device)

    output = generate(char_rnn, device, args.prime_str, args.predict_len, temperature=args.temperature)

    print(output)
