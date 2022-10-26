from ast import Sub
from xpinyin import Pinyin
import argparse
import subprocess
import os

class SubtitleGenerator:
    def __init__(self, model, language, tasks, path, pinyin, pinyin_only):
        self.model = model
        self.language = language
        self.tasks = tasks
        self.pinyin = pinyin
        self.pinyin_only = pinyin_only

        self.path = path if os.path.isabs(path) else os.path.join(os.getcwd(), path)
        self.dir = os.path.dirname(self.path)
        self.name = os.path.splitext(os.path.basename(self.path))[0]

    def translate_to_pinyin(self, path_in, path_out):
        p = Pinyin()
        with open(path_in, 'r', encoding='utf-8') as fin:
            with open(path_out, 'w', encoding='utf-8') as fout:
                for line in fin.readlines():
                    fout.write(p.get_pinyin(line.strip(), ' ', tone_marks='marks') + '\n')

    def generate_subtitles(self, task):
        print(f'Generating [{task}] subtitles for {self.path}')
        subprocess.run([
            'whisper',
            '--model', self.model,
            '--language', self.language,
            '--task', task,
            self.path])

        if task == 'transcribe':
            subtitle_path = f'{os.path.join(self.dir, self.name)}.{self.language}.srt'
        else:
            subtitle_path = f'{os.path.join(self.dir, self.name)}.English.srt'
        os.rename(f'{self.path}.srt', subtitle_path)

        print('Removing .txt and .vtt files')
        os.remove(f'{self.path}.txt')
        os.remove(f'{self.path}.vtt')

        if (self.pinyin or self.pinyin_only) and task == 'transcribe':
            print('Translating Chinese to Pinyin')
            self.translate_to_pinyin(
                subtitle_path,
                f'{os.path.join(self.dir, self.name)}.Pinyin.srt')
            if self.pinyin_only:
                os.remove(subtitle_path)

    def run(self):
        for task in self.tasks:
            self.generate_subtitles(task)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Translate a hanzi file to pinyin')
    parser.add_argument('--path', type=str, required=True)
    parser.add_argument('--model', type=str, default='small')
    parser.add_argument('--language', type=str, default='Chinese')
    parser.add_argument('--task', type=str, default='transcribe')
    parser.add_argument('--pinyin', action='store_true')
    parser.add_argument('--pinyin-only', action='store_true')
    args = parser.parse_args()

    if args.pinyin and args.language != 'Chinese':
        raise Exception('Chinese must be the language if --pinyin is selected')

    s = SubtitleGenerator(
        args.model,
        args.language,
        args.task.split(','),
        args.path,
        args.pinyin,
        args.pinyin_only)
    s.run()