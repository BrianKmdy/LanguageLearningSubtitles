from llsubtitles.dictionaries import chinese

import os
import pytest
import os

dictionary_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'llsubtitles', 'dictionaries', 'data')

@pytest.fixture
def _dictionary():
    yield chinese.ChineseDictionary(os.path.join(dictionary_path, 'chinese-english.json'), 3, 'marks')

def test_translate(_dictionary):
    translation = _dictionary.translate('我是中国人')
    assert translation == [('我', 'wǒ', 'I'), ('是', 'shì', 'is'), ('中国人', 'zhōngguórén', 'Chinese person')]

def test_group_sentence(_dictionary):
    chinese_sentence = '我是中国人'
    assert _dictionary.translate_to_pinyin(chinese_sentence) == 'wǒ shì zhōngguórén'
    assert _dictionary.translate_to_english(chinese_sentence) == 'I is Chinese person'