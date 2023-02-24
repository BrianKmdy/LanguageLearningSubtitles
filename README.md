Language learning application that uses openai's whisper to generate foreign language and English subtitles for videos simultaneously to help with language learning.

# Installation

```bash
> pip install llsubtitles
```

# Usage

To use `llsubtitles` first you need a foreign language .mp4 file. I recommend using [yt-dlp](https://github.com/yt-dlp/yt-dlp) to download content for language learning. Once you have a .mp4 file you can use `llsubtitles` to generate subtitles for it.

```bash
# Using chinese content for this example
> llsubtitles --task translate,transcribe --language Chinese --model small --combined --definitions --pinyin example.mp4
```
**--task**: Refers to the tasks that will be performed by openai's whisper. The options are `translate`, `transcribe`, and `translate,transcribe`. Transcribe will create subtitles in the same language as the source material. Translate will create subtitles in English. Both options are necessary when running with the --combined option.<br>
**--language**: Refers to the language used by openai's whisper to generate subtitles.<br>
**--model**: The model used by whisper. See [their documentation](https://github.com/openai/whisper) for more options.<br>
**--combined**: If this flag is used, the subtitles will be generated in both the foreign language and English.<br>
**--definitions**: If this flag is used, the subtitles will include definitions for the foreign language words.<br>
**--pinyin**: Optional flag for Chinese learners, if this flag is used, the subtitles will include pinyin for the Chinese words.

Note, you should make sure that you have pytorch set up correctly to use Cuda if you're using an Nvidia GPU. See [pytorch's documentation](https://pytorch.org/get-started/locally/) for more information. This will greatly improve performance.

# Credits
Chinese English dictionary is courtesy of [cedict](https://www.mdbg.net/chinese/dictionary?page=cedict)