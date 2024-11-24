import os
import tqdm
import poetree

# see https://github.com/versotym/poetree

def process_poem(args, poem):
    poem_text = ""
    paragraph_id = None

    for line in poem.get_body():
        poem_text += line['text'] + "\n"

        # print extra newline after paragraph
        if paragraph_id != line['id_stanza'] and paragraph_id is not None:
            poem_text += "\n"
        paragraph_id = line['id_stanza']

    if args.without_poem_names:
        text = f"{poem_text}\n"
    else:
        text = f"{poem.title}\n{poem_text}\n"
    return text

def process_corpus(args):

    corpus = poetree.Corpus(args.lang)

    if len(args.filter_author):
        # filter only selected authors
        n_poems = 0
        authors = []
        for author in corpus.get_authors():
            if author.name in args.filter_author:
                n_poems += author.n_poems
                authors += [author]
    else:
        n_poems = corpus.n_poems
        authors = corpus.get_authors()

    with tqdm.tqdm(total=n_poems) as progress_bar:
        for author in authors:

            for poem in author.get_poems():
                progress_bar.set_description(f"{author.name}; {poem.title}")

                text = process_poem(args, poem)

                if args.with_author_names:
                    text = f"{author.name} ({author.born})\n\n" + text
                yield text

                progress_bar.update(1)

def list_authors(args):
    corpus = poetree.Corpus(args.lang)
    for author in corpus.get_authors():
        author_txt = f"{author.name} ({author.born}-{author.died})"
        n_poems_txt = f"Poems: {author.n_poems}"
        cmd_txt = f'--filter-author "{author.name}"'
        print(f"{n_poems_txt:<15}{author_txt:<60}{cmd_txt:<60}")
                
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default="data/export.txt")
    parser.add_argument('--lang', default='cs', help="Corups language")
    parser.add_argument('--filter-author', nargs='+', default=[], help="Limit to only some authors")
    parser.add_argument('--list-authors', action='store_true')
    parser.add_argument('--without-poem-name', action='store_true')
    parser.add_argument('--with-author-name', action='store_true')
    args = parser.parse_args()

    if args.list_authors:
        list_authors(args)
    else:
        if not os.path.exists(os.path.dirname(args.output)):
            os.makedirs(os.path.dirname(args.output))
        with open(args.output, "w", encoding="utf-8") as out:
            for part in process_corpus(args):
                out.write(part)

