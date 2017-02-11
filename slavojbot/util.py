import logging
import io
import json
import os
import re
from math import log

from goose import Goose
from many_stop_words import get_stop_words
from markovify import combine, Text
from markovify.splitters import split_into_sentences
from segtok.segmenter import split_multi
from segtok.tokenizer import word_tokenizer, split_contractions
from slugify import slugify
from snowballstemmer import stemmer


goose = Goose()
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

bracketed_text = re.compile('\[.*\]')
stop_words = list(get_stop_words('en'))
stemmer = stemmer('english')


def slug(text):
    link_stop_words = ['http', 'https', 'www', 'html', 'htm']
    return slugify(text, stopwords=stop_words + link_stop_words)


def get_links():
    links = 'links.txt'
    with open(links) as links:
        return links.read().split('\n')


def get_articles():
    for link in get_links():
        article = load_article(link)
        if not article:
            continue
        yield article


def load_article(url):
    path = 'corpus/' + slug(url)
    if not os.path.exists(path):
        download_article(url, path)
    try:
        with io.open(path, 'r', encoding='utf-8') as f:
            return clean_article(f.read())
    except IOError:
        #download_article(url, path)
        return


def download_article(url, path):
    article = goose.extract(url)
    if not len(article.cleaned_text):
        return
    with io.open(path, 'w', encoding='utf-8') as f:
        f.write(article.cleaned_text)
    logger.info('Downloaded: {}'.format(link))


def clean_article(article, remove_notes=True):
    article = bracketed_text.sub('', article)
    sentences = split_multi(article)
    if remove_notes:
        _sentences = []
        for sentence in sentences:
            if sentence.lower().startswith('notes:'):
                break
            _sentences.append(sentence)
        sentences = _sentences
    return ' '.join(sentences)


def tokenize(sentences, stem=False):
    if not isinstance(sentences, list):
        sentences = split_multi(sentences)
    tokens = [split_contractions(word_tokenizer(sentence)) for
             sentence in sentences]
    word_pattern = re.compile('^[a-z]+$')
    clean_tokens = []
    for token_list in tokens:
        for token in token_list:
            token = token.lower()
            if token in stop_words or not word_pattern.match(token):
                continue
            clean_tokens.append(token)
    if stem:
        return stemmer.stemWords(clean_tokens)
    return clean_tokens


def term_frequencies(tokens):
    denominator = len(tokens)
    return dict((term, 1.0 * tokens.count(term) / denominator)
                for term in set(tokens))


def calculate_idf():
    vs_terms = []
    vs_size = 0
    for article in get_articles():
        tokens = tokenize(article, stem=True)
        vs_terms += list(set(tokens))
        vs_size += 1
    idf_terms = dict((term, 1.0 * log(vs_size / (1 + vs_terms.count(term))))
                     for term in set(vs_terms))
    with open('idf.json', 'w') as f:
        json.dump(idf_terms, f)


def calculate_model():
    models = []
    for article in get_articles():
        try:
            model = Text(article, state_size=2)
        except:
            continue
        models.append(model)
    model = combine(models)
    with open('model.json', 'w') as f:
        f.write(model.to_json())


def load_model():
    with io.open('model.json', 'r', encoding='utf-8') as f:
        model_json = f.read()
        return Text.from_json(model_json)


def load_idf():
    with io.open('idf.json', 'r', encoding='utf-8') as f:
        return json.load(f)


if __name__ == '__main__':
    calculate_model()

