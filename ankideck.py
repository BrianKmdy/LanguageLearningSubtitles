# Tool to generate a deck of anki cards from a subtitle file
from xpinyin import Pinyin
import genanki
import argparse
import json
import uuid

class DeckGenerator:
    def __init__(self, dict_file, max_word_length):
        self.dict_file = dict_file
        self.max_word_length = max_word_length
        self.pinyin = Pinyin()

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
                    pinyin = self.resolve_pinyin(word)
                    yield (word, pinyin, entry['english'])

                    found = True
                    left = right
                    break
            if not found:
                left += 1

    def run(self, subtitle_file):
        my_model = genanki.Model(
            uuid.uuid4().int >> 64 + 1,
            'Simple Model',
            fields=[
                {'name': 'Question'},
                {'name': 'Answer'},
            ],
            templates=[
                {
                'name': 'Card 1',
                'qfmt': '{{Question}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
                },
            ])
        my_deck = genanki.Deck(
            uuid.uuid4().int >> 64 + 1,
            'Chinese test cards')

        with open(subtitle_file, 'r', encoding='utf-8') as f:
            words = set()
            for line in [l.rstrip('\n') for l in f.readlines()]:
                if self.is_chinese(line):
                    for word in self.find_words(line):
                        words.add(word)
            for hanzi, pinyin, english in words:
                my_note = genanki.Note(
                    model=my_model,
                    fields=[pinyin, english])
                my_deck.add_note(my_note)
                print((hanzi, pinyin, english))

        genanki.Package(my_deck).write_to_file('chinese_test_cards.apkg')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate anki deck from subtitle file')
    parser.add_argument('--dict', type=str, required=True)
    parser.add_argument('--sub', type=str, required=True)
    parser.add_argument('--max-word-length', type=int, default=3)
    args = parser.parse_args()

    generator = DeckGenerator(args.dict, args.max_word_length)
    generator.run(args.sub)