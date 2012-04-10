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
            'righthand': 'yuiophjklnm',
            'lefthand': 'qwertasdfgzxcvb',
            'RIGHTHAND': 'YUIOPHJKLNM',
            'LEFTHAND': 'QWERTASDFGZXCVB',
            'symbols': '/@#$%^&*\|[]~`',
            'simplesymbols': "?!-_'",
            'numbers': '23456789',
            }

        self.password_length = 8

        self.rng = Random()

    def generate_char_list(self, password_policy=None):
        """
        """
        character_list = ''

        if not password_policy:
            for k, v in self._characters.iteritems():
                character_list = character_list + v
        else:
            final_characters = self._characters.copy()
            for k, v in password_policy.iteritems():
                if k == "L" and v is False:
                    if 'lefthand' in final_characters:
                        final_characters.pop('lefthand')
                    if 'LEFTHAND' in final_characters:
                        final_characters.pop('LEFTHAND')
                if k == "R" and v is False:
                    if 'righthand' in final_characters:
                        final_characters.pop('righthand')
                    if 'RIGHTHAND' in final_characters:
                        final_characters.pop('RIGHTHAND')
                if k == "U" and v is False:
                    if 'LEFTHAND' in final_characters:
                        final_characters.pop('LEFTHAND')
                    if 'RIGHTHAND' in final_characters:
                        final_characters.pop('RIGHTHAND')
                if k == "l" and v is False:
                    if 'righthand' in final_characters:
                        final_characters.pop('righthand')
                    if 'lefthand' in final_characters:
                        final_characters.pop('lefthand')
                if k == "2" and v is False:
                    if 'numbers' in final_characters:
                        final_characters.pop('numbers')
                if k == "s" and v is False:
                    if 'simplesymbols' in final_characters:
                        final_characters.pop('simplesymbols')
                if k == "S" and v is False:
                    if 'symbols' in final_characters:
                        final_characters.pop('symbols')
            for k, v in final_characters.iteritems():
                try:
                    character_list = character_list + v
                except:
                    pass

        return character_list

    def generate_password(self, password_policy=None):
        """
        """
        password = ""

        all_chars = self.generate_char_list(password_policy)

        for length in range(self.password_length):
            password = password + self.rng.choice(all_chars)

        return password
