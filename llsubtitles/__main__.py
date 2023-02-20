from . import chinese_dictionary
from . import transcribe

import argparse

def main():
    parser = argparse.ArgumentParser(
        description='Translate a hanzi file to pinyin')
    parser.add_argument('path', type=str, nargs='+')
    parser.add_argument('--model', type=str, default='small')
    parser.add_argument('--language', type=str, default='Chinese')
    parser.add_argument('--task', type=str, default='')
    parser.add_argument('--pinyin', action='store_true')
    parser.add_argument('--timed-definitions', action='store_true')
    parser.add_argument('--ranked-definitions', action='store_true')
    parser.add_argument('--tone-marks-subtitles', type=str, default='marks')
    parser.add_argument('--tone-marks-definitions', type=str, default='numbers')
    args = parser.parse_args()

    dictionary = None
    if args.pinyin:
        if args.language != 'Chinese':
            raise Exception(
                'Chinese must be the language if --pinyin is selected')
        print('Loading chinese dictionary')
        dictionary = chinese_dictionary.ChineseDictionary('dictionary.json', 3)

    generator = transcribe.SubtitleGenerator(
        args.model,
        args.language,
        args.task.split(',') if len(args.task) > 0 else [],
        args.pinyin,
        args.timed_definitions,
        args.ranked_definitions,
        dictionary,
        args.tone_marks_subtitles,
        args.tone_marks_definitions)

    for path in args.path:
        generator.generate_subtitles(path)

if __name__ == '__main__':
    main()