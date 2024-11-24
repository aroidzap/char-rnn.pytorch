import os
import argparse
import json
import pathlib
import tqdm

def get_poem(corpus_item, include_poem_name = False):
    poem = '\n\n'.join(['\n'.join([l["text"] for l in p]) for p in corpus_item["body"]])
    if include_poem_name:
        p_title = corpus_item["biblio"]["p_title"]
        if p_title is None:
            p_title = "---"
        poem = p_title + '\n\n' + poem
    return poem + '\n\n'

def process_corpus(args, corpus, num_all_poems, progress_bar, append = False):

    # Filter corpus
    filtered_corpus_text = ""
    num_filtered_poems = 0
    
    extra_info = ""
    if args.p_author_identity is not None:
        extra_info = f" for '{args.p_author_identity}'"
    
    for item in corpus:
        if args.p_author_identity is None or item["p_author"]["identity"].strip().lower() == args.p_author_identity.strip().lower():
            num_filtered_poems += 1
            filtered_corpus_text += get_poem(item, include_poem_name=not args.without_poem_name)
    n_poems_txt = f"Processing corpusCzechVerse, found {num_all_poems + num_filtered_poems} poems{extra_info}"
    # print(n_poems_txt)
    progress_bar.set_description(n_poems_txt)
    
    if len(filtered_corpus_text) or not append:
        # Write
        w = "Appending" if append else "Writing"
        # print(f"{w} filtered output to {args.output}.")
        if not os.path.exists(os.path.dirname(args.output)):
            os.makedirs(os.path.dirname(args.output))
        with open(args.output, "a" if append else "w", encoding="utf-8") as out:
            out.write(filtered_corpus_text)

    return num_all_poems + num_filtered_poems


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--p_author_identity', default=None, help="Erben, Karel Jaromír")
    parser.add_argument('--without-poem-name', action='store_true')
    parser.add_argument('--ccv-download-folder', default="data")
    parser.add_argument('--output', default="data/export.txt")
    args = parser.parse_args()

    # Download corpusCzechVerse


    ccv_path = f"{args.ccv_download_folder}/corpusCzechVerse/ccv"
    if not os.path.exists(ccv_path):
        
        from git import Repo, RemoteProgress
        
        ccv_repo_url = "https://github.com/versotym/corpusCzechVerse.git"
        print(f"Downloading git repo {ccv_repo_url}")
        class GitProgressPrinter(RemoteProgress):
            def update(self, op_code, cur_count, max_count=None, message=""):
                if op_code == 32:
                    print(f"{100 * cur_count / max_count:.1f}% | {message or ''}")
                else:
                    print(f"{cur_count:i} / {max_count:i}")
        Repo.clone_from(ccv_repo_url, f"{args.ccv_download_folder}/corpusCzechVerse", progress=GitProgressPrinter())
        print(f"Done")

    # Load and process whole corpus
    num_all_poems = 0
    files=list(pathlib.Path(ccv_path).rglob("*.json"))

    with tqdm.tqdm(total=len(files)) as progress_bar:
        for i, filename in enumerate(files):
            # print(f"Loading corpus {i+1}/{len(files)}.")
            with open(filename) as file:
                data = json.load(file)
            num_all_poems = process_corpus(args, data, num_all_poems, progress_bar, append = i!=0)
            progress_bar.update(1)
