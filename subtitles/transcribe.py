import chinese_dictionary
import argparse
import subprocess
import os

class SubtitleGenerator:
    def __init__(self, model, language, tasks, pinyin, english, chinese_dictionary=None):
        self.model = model
        self.language = language
        self.tasks = tasks
        self.pinyin = pinyin
        self.english = english
        self.chinese_dictionary = chinese_dictionary

    def _translate_subtitles(self, path_in, path_out, translate_func):
        if self.chinese_dictionary is None:
            raise Exception('Chinese dictionary not provided')
        if not os.path.exists(path_in):
            raise Exception(f'Subtitle file {path_in} does not exist')

        with open(path_in, 'r', encoding='utf-8') as fin:
            with open(path_out, 'w', encoding='utf-8') as fout:
                for line in fin.readlines():
                    fout.write(getattr(self.chinese_dictionary, translate_func)(line.rstrip()) + '\n')

    def _generate_with_whisper(self, task):
        if task not in ('transcribe', 'translate'):
            raise Exception(f'Unknown task {task}')

        print(f'Generating [{task}] subtitles for {self.path}')
        subprocess.run([
            'whisper',
            '--model', self.model,
            '--language', self.language,
            '--task', task,
            self.path])

        if task == 'transcribe':
            os.rename(f'{self.path}.srt', self.generated_subtitle_path)
        else:
            os.rename(f'{self.path}.srt', self.english_subtitle_path)

        print('Removing .txt and .vtt files')
        os.remove(f'{self.path}.txt')
        os.remove(f'{self.path}.vtt')

    def generate_subtitles(self, path):
        self.path = path if os.path.isabs(path) else os.path.join(os.getcwd(), path)
        self.dir = os.path.dirname(self.path)
        self.name = os.path.splitext(os.path.basename(self.path))[0]

        self.generated_subtitle_path = f'{os.path.join(self.dir, self.name)}.{self.language}.srt'
        self.english_subtitle_path = f'{os.path.join(self.dir, self.name)}.English.srt'
        self.pinyin_subtitle_path = f'{os.path.join(self.dir, self.name)}.Pinyin.srt'

        for task in self.tasks:
            print(f'Running task {task}')
            self._generate_with_whisper(task)

        if self.pinyin:
            print('Translating to pinyin')
            self._translate_subtitles(self.generated_subtitle_path, self.pinyin_subtitle_path, 'translate_to_pinyin')
        if self.english:
            print('Translating to english')
            self._translate_subtitles(self.generated_subtitle_path, self.english_subtitle_path, 'translate_to_english')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Translate a hanzi file to pinyin')
    parser.add_argument('path', type=str, nargs='+')
    parser.add_argument('--model', type=str, default='small')
    parser.add_argument('--language', type=str, default='Chinese')
    parser.add_argument('--task', type=str, default='')
    parser.add_argument('--pinyin', action='store_true')
    parser.add_argument('--english', action='store_true')
    args = parser.parse_args()

    dictionary = None
    if args.pinyin or args.english:
        if args.language != 'Chinese':
            raise Exception('Chinese must be the language if --pinyin or --english is selected')
        print('Loading chinese dictionary')
        dictionary = chinese_dictionary.ChineseDictionary(os.environ['DICT_PATH'], 3)

    if args.english and 'translate' in args.task:
        raise Exception('Cannot select both --english and --task translate')

    generator = SubtitleGenerator(
        args.model,
        args.language,
        args.task.split(',') if len(args.task) > 0 else [],
        args.pinyin,
        args.english,
        dictionary)

    for path in args.path:
        generator.generate_subtitles(path)