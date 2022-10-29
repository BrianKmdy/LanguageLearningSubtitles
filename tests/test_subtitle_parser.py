import shutil
import pytest
from subtitles import transcribe
import sys
import os
# TODO Get this import working in a less hacky way
sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '..', 'subtitles'))


@pytest.fixture
def _parser():
    yield transcribe.SubtitleParser()


@pytest.fixture
def _subtitle_file():
    subtitle_file = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'test_data', 'test.srt')
    if not os.path.exists(os.path.dirname(subtitle_file)):
        os.makedirs(os.path.dirname(subtitle_file))

    yield subtitle_file
    shutil.rmtree(os.path.dirname(subtitle_file))


def test_parse_subtitles(_parser, _subtitle_file):
    with open(_subtitle_file, 'w') as f:
        f.writelines([
            '1\n',
            '00:00:00,000 --> 00:00:01,000\n',
            'Hello\n',
            '2\n',
            '00:00:01,000 --> 00:00:02,000\n',
            'World\n',
        ])

    frames = [f for f in _parser.parse_subtitles(_subtitle_file)]
    assert frames[0] == ('1', '00:00:00,000 --> 00:00:01,000', ['Hello'])
    assert frames[1] == ('2', '00:00:01,000 --> 00:00:02,000', ['World'])
