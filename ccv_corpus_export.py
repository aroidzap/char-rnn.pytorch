import os
import argparse
import json
import pathlib
import time

def get_poem(corpus_item, include_poem_name = False):
    poem = '\n\n'.join(['\n'.join([l["text"] for l in p]) for p in corpus_item["body"]])
    if include_poem_name:
        p_title = corpus_item["biblio"]["p_title"]
        if p_title is None:
            p_title = "---"
        poem = p_title + '\n\n' + poem
    return poem + '\n\n'

def process_corpus(args, corpus, num_all_poems, append = False):

    # Filter corpus
    filtered_corpus_text = ""
    num_filtered_poems = 0
    
    extra_info = ""
    if args.p_author_identity is not None:
        extra_info = f" for '{args.p_author_identity}'"
    
    t = time.time()
    print(f"Filtering corpus{extra_info}.")
    for i, item in enumerate(corpus):
        if time.time() - t > 3:
            print(f"Processing corpus items {100 * i / len(corpus):.1f}%.")
            t = time.time()
        if args.p_author_identity is None or item["p_author"]["identity"].strip().lower() == args.p_author_identity.strip().lower():
            num_filtered_poems += 1
            filtered_corpus_text += get_poem(item, include_poem_name=args.with_poem_name)
    print(f"Found {num_all_poems + num_filtered_poems} poems{extra_info}.")
    
    if len(filtered_corpus_text) or not append:
        # Write
        w = "Appending" if append else "Writing"
        print(f"{w} filtered output to {args.output}.")
        if not os.path.exists(os.path.dirname(args.output)):
            os.makedirs(os.path.dirname(args.output))
        with open(args.output, "a" if append else "w", encoding="utf-8") as out:
            out.write(filtered_corpus_text)

    return num_all_poems + num_filtered_poems


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--p_author_identity', default=None, help="Erben, Karel Jaromír")
    parser.add_argument('--with-poem-names', action='store_true')
    parser.add_argument('--ccv-download-folder', default="data")
    parser.add_argument('--output', default="data/export.txt")
    args = parser.parse_args()

    # Download corpusCzechVerse
    if not os.path.exists(args.ccv_download_folder):
        
        from io import BytesIO
        from zipfile import ZipFile
        import requests

        ccv_url = "https://github.com/versotym/corpusCzechVerse/archive/refs/heads/master.zip"
        print(f"Downloading {ccv_url}")
        ccv_zip = ZipFile(BytesIO(requests.get(ccv_url).content))
        print(f"Extracting to {args.ccv_download_folder}")
        if not os.path.exists(os.path.dirname(args.ccv_download_folder)):
            os.makedirs(os.path.dirname(args.ccv_download_folder))
        ccv_zip.extractall(args.ccv_download_folder, strip=True)

    # Load and process whole corpus
    num_all_poems = 0
    files=list(pathlib.Path(f"{args.ccv_download_folder}/corpusCzechVerse-master/ccv").rglob("*.json"))
    for i, filename in enumerate(files):
        print(f"Loading corpus {i+1}/{len(files)}.")
        with open(filename) as file:
            data = json.load(file)
        num_all_poems = process_corpus(args, data, num_all_poems, append = i!=0)
