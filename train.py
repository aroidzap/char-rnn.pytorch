#!/usr/bin/env python
# https://github.com/spro/char-rnn.pytorch

import torch
import torch.nn as nn
from torch.autograd import Variable
import argparse
import os
import random

from tqdm import tqdm

from helpers import *
from model import *
from generate import *

# Parse command line arguments
argparser = argparse.ArgumentParser()
argparser.add_argument('--dataset', type=str, default="data/export.txt")
argparser.add_argument('--model', type=str, default="model/model.pt")
argparser.add_argument('--model_type', type=str, default="gru") # gru, lstm
argparser.add_argument('--n_epochs', type=int, default=2000)
argparser.add_argument('--print_every', type=int, default=100)
argparser.add_argument('--hidden_size', type=int, default=256)
argparser.add_argument('--n_layers', type=int, default=2)
argparser.add_argument('--learning_rate', type=float, default=0.01)
argparser.add_argument('--chunk_len', type=int, default=200)
argparser.add_argument('--batch_size', type=int, default=100)
argparser.add_argument('--shuffle', action='store_true')
argparser.add_argument('--device', type=str, default=None) # cpu, cuda, mps
args = argparser.parse_args()

device = set_torch_device(args.device, verbose=True)

file, file_len = read_file(args.dataset)

def random_training_set(chunk_len, batch_size):
    inp = torch.LongTensor(batch_size, chunk_len)
    target = torch.LongTensor(batch_size, chunk_len)
    for bi in range(batch_size):
        start_index = max(0, random.randint(0, file_len - chunk_len - 1))
        end_index = start_index + chunk_len + 1
        chunk = file[start_index:end_index]
        inp[bi] = char_tensor(chunk[:-1])
        target[bi] = char_tensor(chunk[1:])
    inp = Variable(inp)
    target = Variable(target)
    inp = inp.to(device)
    target = target.to(device)
    return inp, target

def train(inp, target):
    hidden = char_rnn.init_hidden(args.batch_size)
    hidden = hidden.to(device)
    char_rnn.zero_grad()
    loss = 0

    for c in range(args.chunk_len):
        output, hidden = char_rnn(inp[:,c], hidden)
        loss += criterion(output.view(args.batch_size, -1), target[:,c])

    loss.backward()
    char_rnn_optimizer.step()

    return loss.item() / args.chunk_len

def save():
    if not os.path.exists(os.path.dirname(args.model)):
        os.makedirs(os.path.dirname(args.model))
    char_rnn.save(args.model)
    print(f"Saved as {args.model}")

# Initialize models and start training

char_rnn = CharRNN(
    len(ALL_CHARACTERS),
    args.hidden_size,
    len(ALL_CHARACTERS),
    model_type=args.model_type,
    n_layers=args.n_layers,
)
char_rnn_optimizer = torch.optim.Adam(char_rnn.parameters(), lr=args.learning_rate)
criterion = nn.CrossEntropyLoss()

char_rnn.to(device)

start = time.time()
all_losses = []
loss_avg = 0

try:
    print(f"Training for {args.n_epochs} epochs...")
    for epoch in tqdm(range(1, args.n_epochs + 1)):
        loss = train(*random_training_set(args.chunk_len, args.batch_size))
        loss_avg += loss

        if epoch % args.print_every == 0:
            print(f"[{time_since(start)} ({epoch} {epoch / args.n_epochs * 100:.1f}%) {loss:.4f}]")
            print(generate(char_rnn, device), '\n')

    print("Saving...")
    save()

except KeyboardInterrupt:
    print("Saving before quit...")
    save()

