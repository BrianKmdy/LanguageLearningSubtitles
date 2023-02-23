from . import chinese_dictionary

import subprocess
import os
import yaml
import re
from datetime import datetime, timedelta


# A class to generate a definition file from a subtitle file
class SubtitleParser:
    def __init__(self):
        self.frames = None
        self.current = None

        self.frame_index_re = re.compile(
            r'^([0-9]+)$')
        self.frame_time_re = re.compile(
            r'^([0-9]+:[0-9]+:[0-9]+,[0-9]+) --> ([0-9]+:[0-9]+:[0-9]+,[0-9]+)$')
        self.frame_text_re = re.compile(
            r'^(.+)$')

    # Returns a tuple of (index, time, text)
    def parse_subtitles(self, subtitle_file):
        if not os.path.exists(subtitle_file):
            raise Exception(f'Subtitle file {subtitle_file} does not exist')

        self.frames = []
        self.current = None
        with open(subtitle_file, 'r', encoding='utf-8') as fin:
            for line in fin.readlines():
                line = line.strip()
                if self.frame_index_re.match(line):
                    if self.current is not None:
                        yield tuple(self.current)
                    self.current = [line, 'n/a', []]
                elif self.frame_time_re.match(line):
                    match = self.frame_time_re.match(line)
                    self.current[1] = (match.group(1), match.group(2))
                elif self.frame_text_re.match(line):
                    self.current[2].append(line)
            if self.current is not None:
                yield tuple(self.current)


class SubtitleGenerator:
    def __init__(
        self,
        model,
        language,
        tasks,
        pinyin,
        chinese_dictionary,
        tone_marks_subtitles,
        combined,
        definitions
    ):
        self.model = model
        self.language = language
        self.tasks = tasks
        self.pinyin = pinyin
        self.chinese_dictionary = chinese_dictionary
        self.subtitle_parser = SubtitleParser()
        self.tone_marks_subtitles = tone_marks_subtitles
        self.combined = combined
        self.definitions = definitions

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

    def _generate_pinyin_subtitles(self):
        if self.chinese_dictionary is None:
            raise Exception('Chinese dictionary not provided')

        print('Translating to pinyin')
        subtitles = ''
        self.chinese_dictionary.set_tone_marks(self.tone_marks_subtitles)
        for index, time, text in self.subtitle_parser.parse_subtitles(self.generated_subtitle_path):
            subtitles += f'{index}\n{time}\n'
            for line in text:
                subtitles += ' '.join(
                    [pinyin for _, pinyin, _ in self.chinese_dictionary.translate(line)]) + '\n'
            subtitles += '\n'

        with open(self.pinyin_subtitle_path, 'w', encoding='utf-8') as fout:
            fout.write(subtitles.rstrip())

    # Pinyin only at the moment
    def _generate_definition_subtitles(self):
        print('Translating to English')
        subtitles = ''
        self.chinese_dictionary.set_tone_marks(self.tone_marks_subtitles)
        for index, (start_time, end_time), text in self.subtitle_parser.parse_subtitles(self.generated_subtitle_path):
            subtitles += f'{index}\n{start_time} --> {end_time}\n'
            # For each line, show the pinyin and the English translation
            for line in text:
                for _, pinyin, english in self.chinese_dictionary.translate(line):
                    subtitles += f'{pinyin} -> {english}' + '\n'
            subtitles += '\n'

        with open(f'{os.path.join(self.dir, self.name)}.Definitions.srt', 'w', encoding='utf-8') as fout:
            fout.write(subtitles.rstrip())

    def _generate_combined_subtitles(self):
        # Get all frames from subtitle parser for English and Pinyin. Find all overlapping frames and merge them.
        source_frames = list(self.subtitle_parser.parse_subtitles(self.generated_subtitle_path))
        english_frames = list(self.subtitle_parser.parse_subtitles(self.english_subtitle_path))

        # Convert the list of pinyin frames to a dictionary for faster searching
        subtitle_dict = {}
        for _, (start_time, end_time), text in source_frames:
            start_time_epoch = datetime.strptime(start_time, "%H:%M:%S,%f")
            subtitle_dict[start_time_epoch] = {
                'start_time': start_time,
                'end_time': end_time,
                'text': '\n'.join(text)
            }

        # Iterate over English frames, find the closest start time in the subtitle dictionary,
        # and combine the English text with the existing Pinyin text.
        for _, (start_time, end_time), text in english_frames:
            start_time_epoch = datetime.strptime(start_time, "%H:%M:%S,%f")
            closest_start_time = min(subtitle_dict.keys(), key=lambda x: abs(x - start_time_epoch))
            subtitle_dict[closest_start_time]['text'] += '\n' + '\n'.join(text)

        # Write the merged subtitles to a file
        with open(f'{os.path.join(self.dir, self.name)}.Combined.srt', 'w', encoding='utf-8') as fout:
            for i, (_, frame) in enumerate(sorted(subtitle_dict.items())):
                fout.write(f'{i+1}\n')
                fout.write(f'{frame["start_time"]} --> {frame["end_time"]}\n')
                fout.write(f'{frame["text"]}\n\n')

    def generate_subtitles(self, path):
        print(f'Generating subtitles for {path}')
        self.path = path if os.path.isabs(
            path) else os.path.join(os.getcwd(), path)
        self.dir = os.path.dirname(self.path)
        self.name = os.path.splitext(os.path.basename(self.path))[0]

        self.generated_subtitle_path = f'{os.path.join(self.dir, self.name)}.{self.language}.srt'
        self.english_subtitle_path = f'{os.path.join(self.dir, self.name)}.English.srt'
        self.pinyin_subtitle_path = f'{os.path.join(self.dir, self.name)}.Pinyin.srt'

        for task in self.tasks:
            print(f'Running task {task}')
            self._generate_with_whisper(task)

        if self.pinyin:
            self._generate_pinyin_subtitles()
            self.generated_subtitle_path = self.pinyin_subtitle_path

        if self.combined:
            self._generate_combined_subtitles()

        if self.definitions:
            if not self.pinyin():
                raise Exception('Definitions require pinyin subtitles')
            self._generate_definition_subtitles()