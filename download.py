import argparse
import requests

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default="https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt")
    parser.add_argument('--output', default="data/export.txt")
    args = parser.parse_args()
    
    print(f"Downloading '{args.url}' as '{args.output}'.")
    
    with open(args.output, "w") as out:
        out.write(requests.get(args.url).text)

    print("Done.")
    