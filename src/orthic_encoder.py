import os
from typing import List
from glyph import Glyph, SPECIAL_SYMBOLS


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
            if filename == "..png":
                # the period glyph
                glyphs["."] = Glyph(".")
            elif filename.endswith(".png"):
                glyph_name = filename.split(".")[0]
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
                    glyph = self.create_glyph(word, i, glyph_name)
                    result.append(glyph)
                    if glyph.double:
                        i += 2  # Advance by 2 for double letters
                    else:
                        i += len(glyph_name)
                    glyph_added = True
                    break

            if not glyph_added:
                result.append(Glyph("Unknown"))
                i += 1
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
            and not glyph_name
            in SPECIAL_SYMBOLS  # no double-letter dot under, e.g., numbers
        ):
            double = word[index + 1].lower() == word[index].lower()

        return Glyph(glyph_name, capital, double)
