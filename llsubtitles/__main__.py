from . import subtitles
from .dictionaries import chinese

import os
import argparse

dictionary_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dictionaries', 'data')

def main():
    parser = argparse.ArgumentParser(
        description='Create multi-language subtitles from a video file for language learning.')
    parser.add_argument('path', type=str, nargs='+')
    parser.add_argument('--model', type=str, default='small')
    parser.add_argument('--language', type=str, default='Chinese')
    parser.add_argument('--task', type=str, default='')
    parser.add_argument('--pinyin', action='store_true')
    parser.add_argument('--tone-marks-subtitles', type=str, default='marks')
    parser.add_argument('--combined', action='store_true')
    parser.add_argument('--definitions', action='store_true')
    args = parser.parse_args()

    dictionary = None
    if args.pinyin or args.definitions:
        if args.language != 'Chinese':
            raise Exception('Chinese must be the language if --pinyin is selected')
        print('Loading chinese dictionary')
        dictionary = chinese.ChineseDictionary(
            os.path.join(dictionary_path, 'chinese-english.json'), 3)

    generator = subtitles.SubtitleGenerator(
        args.model,
        args.language,
        args.task.split(',') if len(args.task) > 0 else [],
        args.pinyin,
        dictionary,
        args.tone_marks_subtitles,
        args.combined,
        args.definitions)

    for path in args.path:
        generator.generate_subtitles(path)

if __name__ == '__main__':
    main()