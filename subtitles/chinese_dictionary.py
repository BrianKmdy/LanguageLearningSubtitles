# Tool to generate a deck of anki cards from a subtitle file
from xpinyin import Pinyin
import json


class ChineseDictionary:
    def __init__(self, dict_file, max_word_length):
        self.dict_file = dict_file
        self.max_word_length = max_word_length
        self.pinyin = Pinyin()

        with open(self.dict_file) as f:
            dict_raw = json.load(f)
            self.simplified = {e['simplified']: e for e in dict_raw}
            self.traditional = {e['traditional']: e for e in dict_raw}

    @staticmethod
    def is_chinese(line):
        return any(u'\u4e00' <= c <= u'\u9fff' for c in line)

    def _lookup_word_in_dictionary(self, word):
        for dictionary in [self.traditional, self.simplified]:
            if word in dictionary:
                return dictionary[word]
        return None

    def _resolve_pinyin(self, word):
        return self.pinyin.get_pinyin(word, '', tone_marks='marks')

    def _find_words(self, line):
        left = 0
        while left < len(line):
            found = False
            for right in range(min(left + self.max_word_length, len(line)), left, -1):
                word = line[left:right]
                entry = self._lookup_word_in_dictionary(word)
                if entry:
                    pinyin = self._resolve_pinyin(word)
                    yield (word, pinyin, entry['english'])
                    found = True
                    left = right
                    break
            if not found:
                left += 1

    def translate(self, text):
        if self.is_chinese(text):
            return [word for word in self._find_words(text)]
        else:
            return [(text, text, text)]

    def translate_to_pinyin(self, text):
        return ' '.join([pinyin for _, pinyin, _ in self.translate(text)])

    def translate_to_english(self, text):
        return ' '.join([english for _, _, english in self.translate(text)])
