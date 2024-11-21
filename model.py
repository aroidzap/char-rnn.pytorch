# https://github.com/spro/char-rnn.pytorch

import torch
import torch.nn as nn
from torch.autograd import Variable

class CharRNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, model_type="gru", n_layers=1):
        super(CharRNN, self).__init__()
        self.model_type = model_type.lower()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.n_layers = n_layers

        self.encoder = nn.Embedding(input_size, hidden_size)
        if self.model_type == "gru":
            self.rnn = nn.GRU(hidden_size, hidden_size, n_layers)
        elif self.model_type == "lstm":
            self.rnn = nn.LSTM(hidden_size, hidden_size, n_layers)
        self.decoder = nn.Linear(hidden_size, output_size)

    def save(self, model_filename):
        torch.save({
            "input_size": self.input_size,
            "hidden_size": self.hidden_size,
            "output_size": self.output_size,
            "model_type": self.model_type,
            "n_layers": self.n_layers,
            "state_dict": self.state_dict()
        }, model_filename)

    @staticmethod
    def load(model_filename):
        data = torch.load(model_filename, weights_only=True)
        char_rnn = CharRNN(
            data["input_size"], 
            data["hidden_size"], 
            data["output_size"], 
            data["model_type"], 
            data["n_layers"]
        )
        char_rnn.load_state_dict(data["state_dict"])
        return char_rnn

    def forward(self, input, hidden):
        batch_size = input.size(0)
        encoded = self.encoder(input)
        output, hidden = self.rnn(encoded.view(1, batch_size, -1), hidden)
        output = self.decoder(output.view(batch_size, -1))
        return output, hidden

    def forward2(self, input, hidden):
        encoded = self.encoder(input.view(1, -1))
        output, hidden = self.rnn(encoded.view(1, 1, -1), hidden)
        output = self.decoder(output.view(1, -1))
        return output, hidden

    def init_hidden(self, batch_size):
        if self.model_type == "lstm":
            return (Variable(torch.zeros(self.n_layers, batch_size, self.hidden_size)),
                    Variable(torch.zeros(self.n_layers, batch_size, self.hidden_size)))
        return Variable(torch.zeros(self.n_layers, batch_size, self.hidden_size))

