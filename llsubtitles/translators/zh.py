# Tool to generate a deck of anki cards from a subtitle file
from xpinyin import Pinyin
import json


class ChineseDictionary:
    def __init__(self, dict_file, max_word_length, tone_marks='numbers'):
        self.dict_file = dict_file
        self.max_word_length = max_word_length
        self.tone_marks = tone_marks
        self.pinyin = Pinyin()

        self.traditional = {}
        self.simplified = {}
        with open(self.dict_file) as f:
            dict_raw = json.load(f)
            for entry in dict_raw:
                self.traditional.setdefault(entry['traditional'], []).append(entry)
                self.simplified.setdefault(entry['simplified'], []).append(entry)

    @staticmethod
    def is_chinese(line):
        return any(u'\u4e00' <= c <= u'\u9fff' for c in line)

    def _lookup_word_in_dictionary(self, word):
        for dictionary in [self.traditional, self.simplified]:
            if word in dictionary:
                if len(dictionary[word]) > 1:
                    return (word,
                            self._resolve_pinyin(word),
                            '; '.join(sorted([entry['english'] for entry in dictionary[word]], key=lambda e: len(e))))
                else:
                    return (word,
                            self._resolve_pinyin(word),
                            dictionary[word][0]['english'])
        return None

    def _resolve_pinyin(self, word):
        return self.pinyin.get_pinyin(word, '', tone_marks=self.tone_marks)

    def _find_words(self, line):
        left = 0
        while left < len(line):
            found = False
            for right in range(min(left + self.max_word_length, len(line)), left, -1):
                word = line[left:right]
                entry = self._lookup_word_in_dictionary(word)
                if entry:
                    yield entry
                    found = True
                    left = right
                    break
            if not found:
                left += 1

    def set_tone_marks(self, tone_marks):
        self.tone_marks = tone_marks

    def translate(self, text):
        if self.is_chinese(text):
            return [word for word in self._find_words(text)]
        else:
            return [(text, text, text)]

    def translate_to_pinyin(self, text):
        return ' '.join([pinyin for _, pinyin, _ in self.translate(text)])

    def translate_to_english(self, text):
        return ' '.join([english for _, _, english in self.translate(text)])
