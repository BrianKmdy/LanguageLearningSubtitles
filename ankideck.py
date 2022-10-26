# Tool to generate a deck of anki cards from a subtitle file
from xpinyin import Pinyin
import argparse
import json
import re

class DeckGenerator:
    def __init__(self, dict_file, max_word_length):
        self.dict_file = dict_file
        self.max_word_length = max_word_length
        self.pinyin = Pinyin()

#        self.same_re = re.compile(r'.*same as (.*)\[[a-zA-Z1-4]+\]')
#        self.variant_re = re.compile(r'.*variant of (.*)\[[a-zA-Z1-4]+\]')

        with open(self.dict_file) as f:
            dict_raw = json.load(f)
            self.simplified = {e['simplified']: e for e in dict_raw}
            self.traditional = {e['traditional']: e for e in dict_raw}

    # TODO: Parse SRT file correctly instead of looking for Chinese characters
    def is_chinese(self, line):
        return any(u'\u4e00' <= c <= u'\u9fff' for c in line)

    def lookup_word_in_dictionary(self, word):
        for dictionary in [self.traditional, self.simplified]:
            if word in dictionary:
                return dictionary[word]
        return None

#    def resolve_english_definition(self, definition):
#        for re in [self.same_re, self.variant_re]:
#            match = re.match(definition)
#            if match:
#                pass
#                # other_definitions = self.find_words(match[1])
#                # return self.resolve_english_definition(m.group(1))

    def resolve_pinyin(self, word):
        return self.pinyin.get_pinyin(word, '', tone_marks='marks')

    def find_words(self, line):
        left = 0
        while left < len(line):
            found = False
            for right in range(min(left + self.max_word_length, len(line)), left, -1):
                word = line[left:right]
                entry = self.lookup_word_in_dictionary(word)
                if entry:
                    # english = self.resolve_english_definition(entry['english'])
                    pinyin = self.resolve_pinyin(entry['pinyin'])
                    yield (word, pinyin, entry['english'])

                    found = True
                    left = right
                    break
            if not found:
                left += 1

    def run(self, subtitle_file):
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            for line in [l.rstrip('\n') for l in f.readlines()]:
                if self.is_chinese(line):
                    print(line)
                    print([word for word in self.find_words(line)])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate anki deck from subtitle file')
    parser.add_argument('--dict', type=str, required=True)
    parser.add_argument('--sub', type=str, required=True)
    parser.add_argument('--max-word-length', type=int, default=3)
    args = parser.parse_args()

    generator = DeckGenerator(args.dict, args.max_word_length)
    generator.run(args.sub)