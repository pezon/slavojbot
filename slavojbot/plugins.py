from collections import defaultdict
import random
import re

from slackbot.bot import respond_to
from slackbot.bot import listen_to, default_reply
from util import load_model, load_idf, tokenize

model = load_model()
IDF = load_idf()


def get_model_key_candidates(token):
	nonalpha = re.compile('[\W_]+')
	candidates = []
	for key in model.chain.model.keys():
		candidate = ' '.join(key)
		if candidate.lower().startswith(token):
			candidates.append(candidate)
	return list(set(candidates))


def get_token_candidates(terms):
	tokens = tokenize(terms, stem=True)
	population = []
	for token in tokens:
		idf = IDF.get(token)
		if idf > 0:
			for _ in range(int(idf * 100)):
				population.append(token)
	if not tokens:
		tokens = terms.split(' ') # really dumb fallback
	return population


def add_sniffs(text):
	splits = text.split(' ')
	sniffs = random.randint(0, 5)
	for _ in range(0, sniffs):
		index = random.randint(0, len(splits) - 1)
		splits.insert(index, '(sniff)')
	return ' '.join(splits) 


def create_response(term):
	tokens = get_token_candidates(term)
	for tries in range(20):
		try:
			token = random.choice(tokens)
			candidates = get_model_key_candidates(token)
			start = random.choice(candidates)
		except:
			tokens = term.split(' ')
			continue
		response = model.make_sentence_with_start(start)
		if response:
			break
	if not response:
		response = model.make_sentence()
	response = add_sniffs(response)
	return response


@listen_to(r'.*slavoj.*')
def slavoj(message):
    return default_reply(message)


@default_reply
def default_reply(message):
	try:
		text = message.body['text'].encode('utf-8')
		response = create_response(text)
		message.reply(response)
	except:
		message.reply('*snots*')