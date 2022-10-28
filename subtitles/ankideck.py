# Tool to generate a deck of anki cards from a subtitle file
import chinese_dictionary
import genanki
import argparse
import json
import uuid
import os

# TODO Fix the format of cards
# TODO Handle recursive definitions


class AnkiDeckGenerator:
    def __init__(self, chinese_dictionary):
        self.chinese_dictionary = chinese_dictionary

    def _load_template(self, template_file):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(script_dir, 'templates', template_file), 'r') as f:
            return json.load(f)

    def _get_unique_id(self):
        return uuid.uuid4().int >> 64 + 1

    def _translate_subtitles(self, path_in):
        if self.chinese_dictionary is None:
            raise Exception('Chinese dictionary not provided')
        if not os.path.exists(path_in):
            raise Exception(f'Subtitle file {path_in} does not exist')

        words = set()
        with open(path_in, 'r', encoding='utf-8') as fin:
            for line in fin.readlines():
                if self.chinese_dictionary.is_chinese(line):
                    words.update(
                        self.chinese_dictionary.translate(line.rstrip()))
        return words

    def generate_deck(self, subtitle_file, template_file):
        deck_name = subtitle_file.split('.')[0]
        template = self._load_template(template_file)
        model = genanki.Model(
            self._get_unique_id(),
            template['name'],
            fields=template['fields'],
            templates=template['templates'])
        deck = genanki.Deck(
            self._get_unique_id(),
            deck_name)

        for hanzi, pinyin, english in self._translate_subtitles(subtitle_file):
            my_note = genanki.Note(
                model=model,
                fields=[pinyin, english])
            deck.add_note(my_note)

        genanki.Package(deck).write_to_file(f'{subtitle_file.split(".")[0]}.apkg')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate anki deck from subtitle file')
    parser.add_argument('path', type=str, nargs='+')
    parser.add_argument('--anki-template', help='Anki template to use')
    args = parser.parse_args()

    dictionary = chinese_dictionary.ChineseDictionary(
        os.environ['DICT_PATH'], 3)

    generator = AnkiDeckGenerator(dictionary)

    for path in args.path:
        generator.generate_deck(path, args.anki_template)
