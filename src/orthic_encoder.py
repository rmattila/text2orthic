import os
from typing import List
from glyph import Glyph, SPECIAL_SYMBOLS

uses_under_ay = 'd t j q m n v t'.split()


class OrthicEncoder:
    """
    A class to encode English words into sequences of Orthic shorthand glyphs.
    """

    def __init__(self):
        self.glyph_dict = self.load_glyphs()

    def load_glyphs(self):
        """
        Loads glyph images from the resources directory and maps them to their names.

        Returns:
            dict: A dictionary mapping glyph names to Glyph objects.
        """
        glyphs = {}

        for filename in os.listdir("../resources/glyphs"):
            if filename.endswith(".png"):
                glyph_name = filename[:-4]
                glyphs[glyph_name] = Glyph(glyph_name)

        return glyphs

    def encode_word(self, word: str) -> List[Glyph]:
        """
        Encodes a given English word into a sequence of Orthic shorthand glyphs.

        Args:
            word (str): The word to encode.

        Returns:
            list: A list of Glyph objects representing the encoded word.
        """
        if word.lower() in ["l", "l."]:
            result = [Glyph("l_standalone")]
            if len(word) > 1:
                result.append(Glyph("."))
            return result

        if word.lower() in ["s", "s."]:
            result = [Glyph("s_straight")]
            if len(word) > 1:
                result.append(Glyph("."))
            return result

        result = []
        i = 0
        while i < len(word):
            glyph_added = False
            for glyph_name in sorted(self.glyph_dict.keys(), key=len, reverse=True):
                next_index = i + len(glyph_name)

                # Check if the next character forms a double letter with the last in
                # this glyph
                forms_double = (
                    next_index < len(word)
                    and word[next_index].lower() == word[next_index - 1].lower()
                )

                # Skip this glyph if it would absorb a double letter
                #
                # An example is "ISSUE", which we want to parse to
                # [I][S-double][U][E] and not [IS][S][U][E]
                # if an IS-glyph exists
                if forms_double and len(glyph_name) > 1:
                    continue

                if word[i:].lower().startswith(glyph_name):
                    advance = len(glyph_name)
                    if glyph_name == 'ay' and i > 0 and word[i-1].lower() in uses_under_ay or i > 1 and word[i-2:i].lower() in uses_under_ay:
                        glyph_name = 'ay_under'
                    elif glyph_name == 'w' and (i == 0 or (len(word) > i+1 and word[i+1].lower() == 'l')):
                        glyph_name = 'w_initial'
                    glyph = self.create_glyph(word, i, glyph_name)
                    result.append(glyph)
                    if glyph.double:
                        advance = 2
                    i += advance
                    glyph_added = True
                    break

            if not glyph_added:
                result.append(Glyph("Unknown"))
                i += 1
        if result[-2:] == [Glyph('w'), Glyph('s')] or result[-2:] == [Glyph('w_initial'), Glyph('s')]:
            result[-2] = Glyph('ws_final')
            result.pop()
        return result

    def create_glyph(self, word, index, glyph_name):
        """
        Creates a Glyph object for a specific part of the word. This method checks if the
        corresponding part of the word is a capital letter or if it's a repeated letter that
        should be marked as a double glyph.

        Args:
            word (str): The word being encoded.
            index (int): The current index in the word, indicating where the glyph starts.
            glyph_name (str): The name of the glyph being created.

        Returns:
            Glyph: A Glyph object initialized with the symbol, and flags for capitalization
            and doubling set as needed.
        """
        capital = word[index : index + len(glyph_name)].isupper()

        double = False
        if (
            len(glyph_name) == 1
            and index + 1 < len(word)
            and glyph_name
            not in SPECIAL_SYMBOLS  # no double-letter dot under, e.g., numbers
        ):
            double = word[index + 1].lower() == word[index].lower()

        return Glyph(glyph_name, capital, double)
