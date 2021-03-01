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
import json
import pprint as pp
import logging
import subprocess

import nltk # Natural Language Toolkit (https://www.nltk.org)
from nltk.tokenize import sent_tokenize, word_tokenize

import duden # python module which can provide various information about given german word
# ~ from demorphy import Analyzer # DEMorphy is a morphological analyzer for German language (https://github.com/DuyguA/DEMorphy)
# ~ from demorphy.tagset import ParsedResult
# ~ import spacy # spaCy is library for advanced Natural Language Processing in Python (https://spacy.io)

# ~ from mydict import PersonalDictionary

from kb4it.services.builder import KB4ITBuilder

class MyFilter(logging.Filter):
    def filter(self, record):
        print("RECORD NAME: %s" % record.name)
        if record.name != 'Theme':
            return False
        return True

class Theme(KB4ITBuilder):
    envvars = {}
    cache = {}
    nlp = None
    # ~ pd = PersonalDictionary()

    def generate_sources(self):
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        # ~ self.log.addFilter(MyFilter())
        self.check_environment()
        self.initialize_environment()
        self.analyze_userdata()

    def build(self):
        """Create standard pages for default theme"""
        self.create_page_dictionary()
        # ~ self.create_page_properties()
        # ~ self.create_page_stats()
        # ~ self.create_page_index_all()
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
                    self.log.debug(filepath)
                    text = open(filepath, 'r').read()
                    self.analyze_text(topic, text)
                    # ~ for doc in tobj:
                        # ~ for key in tobj[doc]:
                            # ~ self.cache['letters'].add(key[0].upper())
                            # ~ if tobj[doc][key]['poskey'] == 'NOUN':
                                # ~ if not key in self.cache['topics'][topic]:
                                    # ~ keys = self.cache['topics'][topic]
                                    # ~ keys.append(key)
                                    # ~ self.cache['topics'][topic] = sorted(keys)
            except NotADirectoryError:
                continue

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

    def analyze_text(self, topic, text):
        words = set()

        self.load_global_cache()

        for sentence in nltk.sent_tokenize(text):
            words = words.union([word for word in word_tokenize(sentence) if word.isalpha()])

        self.log.debug("Analyzing %d words", len(words))
        for word in sorted(words):
            if not word in self.cache['words']: # check if word is not in global cache
                self.log.warning("[ ? ] Word '%s' not found in global cache", word)
                match = duden.get(word)
                if match is None:
                    self.log.warning("[ ? ] Word '%s' not found in duden cache", word)
                    found = duden.search(word, exact=False)
                    if len(found) > 0:
                        match = found[0]
                        try:
                            self.cache['words'][word] = match.export()
                        except:
                            self.log.error("[ ! ] Something went wrong with word '%s", word)
                        self.log.info("[ + ] Word '%s' found in duden dictionary and added to global cache", word)
                    else:
                        self.log.info("[ - ] Word '%s' not found", word)
                else:
                    try:
                        self.cache['words'][word] = match.export()
                    except:
                        self.log.error("[ ! ] Something went wrong with word '%s", word)
                    self.log.info("[ + ] Word '%s' found in duden dictionary and added to global cache", word)

            else:
                key = self.cache['words'][word]
                self.log.info("[ = ] Word '%s' got from cache" % word)

            try:
                try:
                    topics = self.cache['words'][word]['topic']
                    if not topic in topics:
                        topics.append(topic)
                    self.cache['words'][word]['topic'] = sorted(topics)
                except:
                    self.cache['words'][word]['topic'] = [topic]
            except KeyError:
                pass

            self.save_global_cache()

    def create_page_index(self):
        var = {}
        TPL_INDEX = self.template('PAGE_INDEX')
        var['title'] = 'Deutschkurs'
        self.distribute('index', TPL_INDEX.render(var=var))

    def create_page_dictionary(self):
        TPL_INDEX = self.template('PAGE_DICTIONARY')

        # Get all letters
        letters = set()
        for word in self.cache['words']:
            letters.add(word[0].upper())

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
            self.log.debug(var['dictionary'])
            self.distribute('dictionary-%s' % letter, TPL_INDEX.render(var=var))

    # ~ def create_page_dictionary(self):
        # ~ var = {}
        # ~ TPL_INDEX = self.template('PAGE_DICTIONARY')
        # ~ var['title'] = 'Dictionary'
        # ~ letters = set()
        # ~ dictionary = {}
        # ~ for word in self.cache['words']:
            # ~ letter = word[0].upper()
            # ~ letters.add(letter)
            # ~ if letter in dictionary:
                # ~ words = dictionary[letter]
                # ~ words.append(word)
                # ~ dictionary[letter] = sorted(words)
            # ~ else:
                # ~ dictionary[letter] = [word]


        # ~ var['letters'] = sorted(list(letters))
        # ~ var['dictionary'] = dictionary
        # ~ var['cache'] = self.cache
        # ~ self.distribute('dictionary', TPL_INDEX.render(var=var))

    def create_page_about_app(self):
        var = {}
        PAGE_ABOUT_APP = self.template('PAGE_ABOUT_APP')

        var['theme'] = self.srvapp.get_theme_properties()
        var['content'] = 'No info available'
        self.distribute('about_app', PAGE_ABOUT_APP.render(var=var))
