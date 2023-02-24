# Tool to generate a deck of anki cards from a subtitle file
from xpinyin import Pinyin
import json


class ChineseDictionary:
    def __init__(
            self,
            dict_file: str,
            max_word_length: int,
            tone_marks :str='numbers'
    ):
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
    def is_chinese(line: str):
        return any(u'\u4e00' <= c <= u'\u9fff' for c in line)

    def _lookup_word_in_dictionary(self, word: str):
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

    def _resolve_pinyin(self, word: str):
        return self.pinyin.get_pinyin(word, '', tone_marks=self.tone_marks)

    def _find_words(self, line: str):
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

    def set_tone_marks(self, tone_marks: str):
        self.tone_marks = tone_marks

    def translate(self, text: str):
        if self.is_chinese(text):
            return [word for word in self._find_words(text)]
        else:
            return [(text, text, text)]

    def translate_to_pinyin(self, text: str):
        return ' '.join([pinyin for _, pinyin, _ in self.translate(text)])

    def translate_to_english(self, text: str):
        return ' '.join([english for _, _, english in self.translate(text)])
