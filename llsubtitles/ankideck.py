# Tool to generate a deck of anki cards from a subtitle file
from . import chinese_dictionary
from . import transcribe

import genanki
import argparse
import json
import uuid
import os

# TODO Handle recursive definitions
# TODO Return all definitions for a given character


class AnkiDeckGenerator:
    def __init__(self, chinese_dictionary):
        self.chinese_dictionary = chinese_dictionary
        self.subtitle_parser = transcribe.SubtitleParser()

    def _load_template(self, template_file):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(script_dir, 'templates', template_file), 'r') as f:
            return json.load(f)

    def _get_unique_id(self):
        return uuid.uuid4().int >> 64 + 1

    def _get_translations(self, subtitle_file):
        # Generate the translations for the cards
        translations = set()
        for _, _, text in self.subtitle_parser.parse_subtitles(subtitle_file):
            for line in text:
                for _, pinyin, english in self.chinese_dictionary.translate(line):
                    translations.add((pinyin, english))
        return translations

    def generate_deck(self, subtitle_file, template_file):
        print(f'Generating deck from {subtitle_file}')
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

        for translation in self._get_translations(subtitle_file):
            note = genanki.Note(
                model=model,
                fields=translation)
            deck.add_note(note)

        genanki.Package(deck).write_to_file(
            f'{subtitle_file.split(".")[0]}.apkg')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate anki deck from subtitle file')
    parser.add_argument('path', type=str, nargs='+')
    parser.add_argument('--anki-template', help='Anki template to use')
    parser.add_argument('--tone-marks', default='marks', help='Tone marks to use')
    args = parser.parse_args()

    dictionary = chinese_dictionary.ChineseDictionary(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dictionary.json'), 3, args.tone_marks)

    generator = AnkiDeckGenerator(dictionary)

    for path in args.path:
        generator.generate_deck(path, args.anki_template)
