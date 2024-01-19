# MediaFormatter: Effortless Video and Subtitle Handling at Your Fingertips

Welcome to MediaFormatter, a lean yet powerful command-line interface (CLI). It enables you to manage media files with ease. Regardless of whether you are a seasoned developer or a beginner, MediaFormatter offers an effortless approach to managing videos and subtitles like never before.

## Exciting Features

**Rename with Ease**: Organize your media collection effortlessly. Batch rename video files and subtitles following a specific format such as "Title.of.the.TV.Series.SXXEXX".

**Tailor-Made Styles**: Personalize your viewing by customizing the styles of `.ass` subtitle files. Adjust everything from font name to color, boldness, and even italicization. Added bonus: you can personalize styles for different languages!

**Preprocess, Merge and Tag**: Choose your preferred audio/video tracks and merge them with subtitles. Add language tags to subtitles and combine attachments including font files.

**Text-Based Subtitle Conversion and Extraction**: Presently, MediaFormatter supports the extraction of subtitles and conversion between text-based formats like `.ass` and `.srt`. The power to convert and extract subtitles gives you greater flexibility in how you choose to use them.

**Perfect Alignment**: Sync your subtitles flawlessly to the video stream by adjusting their timestamps.

The best part? With MediaFormatter, you can perform these operations on individual files or on multiple files at once - your choice!

*Note: We're considering leveraging advanced technologies like object detection and text recognition to extract and convert text from more complex sources like PGS subtitles or on-screen displayed text in the future.*

## Unleashing the Power of MediaFormatter

Using MediaFormatter is as simple as typing `mf`, followed by your command, arguments, and options:

```bash
mf <command> <args> <options>
```
Imagine you need to extract all subtitle tracks from a whole season of your favorite show:

```bash
mf extract Friends.S01 --all
```
In this command, `extract` informs MediaFormatter what to do, `Friends.S01` tells it where the videos are, and `--all` commands it to process every file in the folder. Sit back and watch as MediaFormatter extracts all subtitle tracks, renames them to match their corresponding video, and appends an identification for the language along with a `.ass` extension.

## Noteworthies

Batch processing is a gem, but sometimes you might encounter errors. Don't panic - MediaFormatter is designed to continue processing the remaining files. A comprehensive logging system has your back, keeping track of all operations and helping identify any issues.

---

Get ready to experience media handling like never before with MediaFormatter!