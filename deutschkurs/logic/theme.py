#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Server module.

# File: theme.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: default theme script
"""

# Standard libraries
import os
import glob
import json
import pprint as pp
import logging
import subprocess

import nltk # Natural Language Toolkit (https://www.nltk.org)
from nltk.tokenize import sent_tokenize, word_tokenize

import duden # python module which can provide various information about given german word
# ~ from demorphy import Analyzer # DEMorphy is a morphological analyzer for German language (https://github.com/DuyguA/DEMorphy)
# ~ from demorphy.tagset import ParsedResult
import spacy # spaCy is library for advanced Natural Language Processing in Python (https://spacy.io)

try:
    # ~ msg.debug("Loading German corpus")
    # ~ nlp = spacy.load("de_core_news_lg")
    nlp = spacy.load("de_dep_news_trf")
except:
    # ~ msg.error("German corpus not found. Download it manually:")
    # ~ msg.info("python3 -m spacy download de_dep_news_trf")
    # python3 -m spacy download de_core_news_sm
    exit(-1)


from kb4it.services.builder import KB4ITBuilder

TITLE = "= %s\n\n"
PROP = ":%s:\t\t%s\n"
EOHMARK = "// END-OF-HEADER. DO NOT MODIFY OR DELETE THIS LINE\n\n"
BODY = "%s"


class Theme(KB4ITBuilder):
    envvars = {}
    cache = {}
    stats = {}
    nlp = None
    # ~ pd = PersonalDictionary()

    def clean_sources_dir(self):
        sources = glob.glob(os.path.join(self.envvars['DIRS']['ROOT'], '*.adoc'))
        for adoc in sources:
            os.unlink(adoc)

    def generate_sources(self):
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        self.check_environment()
        self.initialize_environment()
        self.clean_sources_dir()
        self.analyze_userdata()
        for word in self.cache['words']:
            self.create_page_word(word)


    def build(self):
        """Create standard pages for default theme"""
        self.create_page_dictionary()
        self.create_page_topics()
        self.create_page_pos()
        self.create_page_grammar()
        self.create_page_index()
        self.create_page_about_app()
        self.create_page_about_theme()
        self.create_page_about_kb4it()
        self.create_page_help()


    def check_environment(self):
        try:
            nltk.data.find('tokenizers/punkt')
            self.log.debug("[CHECKS] - Tokenizer Punkt found!")
        except LookupError as error:
            self.log.warning("[CHECKS] - Tokenizer Punkt not found! Downloading...")
            nltk.download('punkt')
            self.log.info("[SETUP] - Tokenizer Punkt for NLTK downloaded")

        self.envvars['DIRS'] = {}
        self.envvars['FILE'] = {}

        # Check directories existence
        ROOT = self.srvapp.get_source_path()
        self.envvars['DIRS']['ROOT'] = ROOT

        ## Words Cache
        DIR_CACHE = os.path.join(ROOT, 'resources', 'cache')
        if not os.path.exists(DIR_CACHE):
            os.makedirs(DIR_CACHE)
            self.log.debug("[SETUP] - Directory 'cache' created")
        self.envvars['DIRS']['CACHE'] = DIR_CACHE

        ## Dictionary definitions
        DIR_DICT = os.path.join(ROOT, 'resources', 'dict')
        if not os.path.exists(DIR_DICT):
            os.makedirs(DIR_DICT)
        self.envvars['DIRS']['DICT'] = DIR_DICT


        ## User data
        DIR_USERDATA = os.path.join(ROOT, 'resources', 'userdata')
        self.envvars['DIRS']['USERDATA'] = DIR_USERDATA
        if not os.path.exists(DIR_USERDATA):
            os.makedirs(DIR_USERDATA)
            # Write README
            with open(os.path.join(DIR_USERDATA, 'README'), 'w') as fout:
                fout.write("Each directory is a topic. Give them a meaninful name\n")
            # Write example
            os.makedirs(os.path.join(DIR_USERDATA, 'grundschule'))
            with open(os.path.join(DIR_USERDATA, 'grundschule', 'info-20200901.txt'), 'w') as fout:
                sentences = """Liebe Eltern.\n
                            Im Anhang finden Sie die Infos zum Infektionsschutzgesetz.\n
                            Vielen Dank und noch einen schönen Tag!\n
                            Grüße"""
                fout.write(sentences)

        # Global cache for words
        FILE_CACHE = os.path.join(self.envvars['DIRS']['CACHE'], 'cache.json')
        self.envvars['FILE']['CACHE'] = FILE_CACHE

    def initialize_environment(self):
        self.load_global_cache()

    def analyze_userdata(self):
        for topic in os.listdir(self.envvars['DIRS']['USERDATA']):
            if not topic in self.cache['topics']:
                self.cache['topics'][topic] = []
            topicpath = os.path.join(self.envvars['DIRS']['USERDATA'], topic)
            try:
                for filename in os.listdir(topicpath):
                    filepath = os.path.join(topicpath, filename)
                    self.log.info("Topic[%s] - File[%s]", topic, filename)
                    text = open(filepath, 'r').read()
                    self.analyze_text(topic, text)
            except NotADirectoryError:
                continue
        self.create_stats()

    def load_global_cache(self):
        try:
            with open(self.envvars['FILE']['CACHE'], 'r') as fc:
                self.cache = json.load(fc)
                self.log.debug("Global cache loaded: %d words", len(self.cache['words']))
        except:
            self.cache = {}
            self.cache['words'] = {}
            self.cache['topics'] = {}
            with open(self.envvars['FILE']['CACHE'], 'w') as fc:
                json.dump(self.cache, fc)
                # ~ self.log.debug("Words cache created")

    def save_global_cache(self):
        with open(self.envvars['FILE']['CACHE'], 'w') as fc:
            json.dump(self.cache, fc)
            # ~ self.log.debug("Words cache saved")

    def get_duden_dict(self, word):
        self.log.debug("Looking for: %s", word)
        ddict = {}
        match = duden.get(word)
        if match is None:
            self.log.warning("[ ? ] Word '%s' not found in duden cache", word)
            found = duden.search(word, exact=False)
            if len(found) > 0:
                match = found[0]
                self.log.warning("[ < ] Word '%s' found in duden dictionary", word)
                try:
                    ddict = match.export()
                    self.log.info("[ + ] Word '%s' added to global cache", word)
                except:
                    self.log.error("[ ! ] Something went wrong with word '%s", word)
            else:
                self.log.info("[ - ] Word '%s' not found", word)
                ddict = None
        else:
            try:
                ddict = match.export()
            except:
                # duden bug
                ddict = None
        return ddict

    def is_word(self, word):
        # "16.02.2021." is detected as a ADJ??
        ans = True
        for letter in word:
            ans = ans and not letter.isdigit()
        return ans

    def analyze_text(self, topic, text):
        words = set()

        self.load_global_cache()

        self.log.debug("Analyzing %d words", len(words))
        doc = nlp(text)
        for word in doc:
            # ~ print(dir(word))
            # ~ print(word.lemma_)
            # ~ print(word.norm_)
            # ~ print(word.prefix_)
            # ~ print(word.sent)
            # ~ print(word.tag_)
            # ~ print(word.text)
            # ~ print(word.text_with_ws)
            # ~ print(word.vocab)

            if not word.pos_ in ['PUNCT', 'SPACE', 'NUM'] and self.is_word(word.text):
                key = word.text.lower()
                # ~ self.log.debug("%s -> %s (%s)", key, word.pos_, spacy.explain(word.pos_))
                if key not in self.cache['words']:
                    self.cache['words'][key] = {}
                    self.cache['words'][key]['title'] = word.text
                    # ~ self.cache['words'][key]['part_of_speech'] = spacy.explain(word.pos_).title()

                    # If substantive, get genre from duden
                    if word.pos_ == 'NOUN':
                        ddict = self.get_duden_dict(word.text)
                        if ddict is not None:
                            for k in ddict:
                                self.cache['words'][key][k] = ddict[k]

                    try:
                        article = self.cache['words'][key]['article']
                    except:
                        self.cache['words'][key]['article'] = ''
                    self.cache['words'][key]['part_of_speech'] = spacy.explain(word.pos_).title()


                    #topics
                    try:
                        topics = self.cache['words'][key]['topic']
                        if not topic in topics:
                            topics.append(topic)
                        self.cache['words'][key]['topic'] = sorted(topics)
                    except:
                        self.cache['words'][key]['topic'] = [topic]

            self.save_global_cache()


    # ~ def analyze_text(self, topic, text):
        # ~ words = set()

        # ~ self.load_global_cache()

        # ~ for sentence in nltk.sent_tokenize(text):
            # ~ words = words.union([word for word in word_tokenize(sentence) if word.isalpha()])

        # ~ self.log.debug("Analyzing %d words", len(words))
        # ~ for word in sorted(words):
            # ~ if not word in self.cache['words']: # check if word is not in global cache
                # ~ self.log.warning("[ ? ] Word '%s' not found in global cache", word)
                # ~ match = duden.get(word)
                # ~ if match is None:
                    # ~ self.log.warning("[ ? ] Word '%s' not found in duden cache", word)
                    # ~ found = duden.search(word, exact=False)
                    # ~ if len(found) > 0:
                        # ~ match = found[0]
                        # ~ self.log.warning("[ < ] Word '%s' found in duden dictionary", word)
                        # ~ try:
                            # ~ self.cache['words'][word] = match.export()
                            # ~ self.log.info("[ + ] Word '%s' added to global cache", word)
                        # ~ except:
                            # ~ self.log.error("[ ! ] Something went wrong with word '%s", word)
                    # ~ else:
                        # ~ self.log.info("[ - ] Word '%s' not found", word)
                # ~ else:
                    # ~ try:
                        # ~ self.cache['words'][word] = match.export()
                    # ~ except:
                        # ~ self.log.error("[ ! ] Something went wrong with word '%s", word)
                    # ~ self.log.info("[ + ] Word '%s' found in duden dictionary and added to global cache", word)

            # ~ else:
                # ~ key = self.cache['words'][word]
                # ~ self.log.info("[ = ] Word '%s' got from cache" % word)

            # ~ try:
                # ~ try:
                    # ~ topics = self.cache['words'][word]['topic']
                    # ~ if not topic in topics:
                        # ~ topics.append(topic)
                    # ~ self.cache['words'][word]['topic'] = sorted(topics)
                # ~ except:
                    # ~ self.cache['words'][word]['topic'] = [topic]
            # ~ except KeyError:
                # ~ pass

            # ~ try:
                # ~ if self.cache['words'][word]['part_of_speech'].startswith('Substantiv'):
                    # ~ p, g = self.cache['words'][word]['part_of_speech'].split(',')
                    # ~ self.cache['words'][word]['part_of_speech'] = p
                    # ~ self.cache['words'][word]['genre'] = g.strip().title()
                # ~ else:
                    # ~ self.cache['words'][word]['genre'] = None
            # ~ except:
                # ~ self.cache['words'][word] = {}
                # ~ del(self.cache['words'][word])

            # ~ self.save_global_cache()

    def create_stats(self):
        self.stats['len_words'] = len(self.cache['words'])
        self.stats['topics'] = {}
        self.stats['len_topics'] = 0
        self.stats['pos'] = {}
        for word in self.cache['words']:
            # topics
            for topic in self.cache['words'][word]['topic']:
                try:
                    n = self.stats['topics'][topic]
                    n += 1
                    self.stats['topics'][topic] = n
                except:
                    self.stats['topics'][topic] = 1

            # Part of speech
            pos = self.cache['words'][word]['part_of_speech']
            try:
                n = self.stats['pos'][pos]
                n += 1
                self.stats['pos'][pos] = n
            except:
                self.stats['pos'][pos] = 1

        self.stats['len_topics'] = len(self.stats['topics'])
        self.stats['len_pos'] = len(self.stats['pos'])

    def create_page_index(self):
        var = {}
        TPL_INDEX = self.template('PAGE_INDEX')
        var['title'] = 'Deutschkurs'
        self.distribute('index', TPL_INDEX.render(var=var))

    def create_page_dictionary(self):
        TPL_DICTIONARY = self.template('PAGE_DICTIONARY')
        TPL_DICTIONARY_LETTER = self.template('PAGE_DICTIONARY_LETTER')

        # Get all letters
        letters = set()
        for word in self.cache['words']:
            letters.add(word[0].upper())

        var = {}
        var['title'] = 'Dictionary'
        var['letters'] = sorted(list(letters))
        var['topics'] = self.create_tagcloud_from_key('Topic')
        var['pos'] = self.create_tagcloud_from_key('Part Of Speech')
        # ~ self.log.error("TOPICS: %s", var['topics'])
        var['stats'] = self.stats
        self.distribute('dictionary', TPL_DICTIONARY.render(var=var))

        for letter in letters:
            var = {}
            dictionary = {}
            var['title'] = 'Dictionary'
            for word in self.cache['words']:
                wfl = word[0].upper()
                if wfl == letter:
                    try:
                        words = dictionary[letter]
                        words.append(word)
                        dictionary[letter] = sorted(words)
                    except:
                        dictionary[letter] = [word]

            var['letters'] = sorted(list(letters))
            var['dictionary'] = dictionary
            var['cache'] = self.cache
            var['letter-active'] = letter
            self.distribute('dictionary-%s' % letter, TPL_DICTIONARY_LETTER.render(var=var))

    def create_page_topics(self):
        TPL_TOPICS = self.template('PAGE_TOPICS')
        var = {}
        var['title'] = 'Topics'
        var['topics'] = self.create_tagcloud_from_key('Topic')
        self.distribute('topics', TPL_TOPICS.render(var=var))

    def create_page_pos(self):
        TPL_POS = self.template('PAGE_POS')
        var = {}
        var['title'] = 'Parts of Speech'
        var['pos'] = self.create_tagcloud_from_key('Part Of Speech')
        self.distribute('pos', TPL_POS.render(var=var))

    def create_page_grammar(self):
        TPL_GRAMMAR = self.template('PAGE_GRAMMAR')
        var = {}
        var['title'] = 'Grammar'
        self.distribute('grammar', TPL_GRAMMAR.render(var=var))

    def build_property(self, key, value):
        try:
            return PROP % (key, value)
        except:
            return ''

    def create_page_word(self, word):
        # ~ self.log.info("Creating page for word: %s", self.cache['words'][word])
        doc_path = os.path.join(self.envvars['DIRS']['ROOT'], "word_%s.adoc" % word)
        with open(doc_path, 'w') as fdp:
            fdp.write(TITLE % self.cache['words'][word]['title'])
            # ~ fdp.write(PROP % (cache['words'][word]['pos'], cache['words'][word]['word']))
            fdp.write(self.build_property("Topic", ', '.join(self.cache['words'][word]['topic'])))
            fdp.write(self.build_property("Part Of Speech", self.cache['words'][word]['part_of_speech']))
            # ~ fdp.write(self.build_property("Genre", self.cache['words'][word]['genre']))
            fdp.write(EOHMARK)
            # ~ fdp.write(BODY % self.cache['words'][word]['meaning_overview'])
            self.log.info("Page created for word: %s", word)

    def create_page_about_app(self):
        var = {}
        PAGE_ABOUT_APP = self.template('PAGE_ABOUT_APP')

        var['theme'] = self.srvapp.get_theme_properties()
        var['content'] = 'No info available'
        self.distribute('about_app', PAGE_ABOUT_APP.render(var=var))
