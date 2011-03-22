#!/usr/bin/env python
"""
A simple script for making random passwords, WITHOUT 1,l,O,0.  Because
those characters are hard to tell the difference between in some fonts.

"""

import sys
from random import Random

class random_password(object):

    def __init__(self):
        self._characters = {
            'righthand_noncaps': 'yuiophjklnm',
            'lefthand_noncaps': 'qwertasdfgzxcvb',
            'righthand_caps': 'YUIOPHJKLNM',
            'lefthand_caps': 'QWERTASDFGZXCVB',
            'symbols': '/@#$%^&*\|[]~`',
            'simplesymbols': "?!-_'",
            'numbers': '23456789',
            }

        self.password_length = 8

        self.rng = Random()

    def generate_char_list(self, character_selection='all'):
        """
        """
        character_list = ''

        if character_selection.lower() == 'all':
            for k, v in self._characters.iteritems():
                character_list = character_list + v
        else:
            for option in character_selection.split(","):
                try:
                    character_list = character_list + self.characters[option.strip()]
                except:
                    pass

        return character_list

    def generate_password(self):
        """
        """
        password = ""

        all_chars = self.generate_char_list()

        for length in range(self.password_length):
            password = password + self.rng.choice(all_chars)

        return password
