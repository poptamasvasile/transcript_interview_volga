# Audio Transcription Pipeline

A small Python pipeline that transcribes audio files using the AssemblyAI API and returns both the full transcript and sentence-level segments with timestamps.

## Overview

The pipeline has three stages:

1. **Load & validate** the audio file (`AudioLoader`)
2. **Transcribe** it via the AssemblyAI API (`transcribe`)
3. **Extract** sentence-level segments with start/end timestamps (`get_segments`)

Each stage is independent and communicates with the next through simple types — a file path, a `Transcript` object, and a list of dictionaries — so the stages don't leak implementation details into each other.

## Design Decisions

### Three separate stages

I split the pipeline into three stages — load and validation, transcription, and post-processing — so each piece is independent and replaceable. Swapping AssemblyAI for another transcription provider only touches `transcribe()`. Adding a new output format, like word-level timestamps or SRT subtitles, only touches `get_segments()`. Changing the set of accepted input formats only touches `AudioLoader`. This separation makes the code easier to test, easier to extend, and easier to reason about.

### Class for the loader, functions for the rest

`AudioLoader` is a class because it holds state — the validated file path — and has a clear lifecycle: construct, validate, use. Transcription and segment extraction, on the other hand, are pure transformations with no state to manage, so plain functions are simpler.

### Fail fast on invalid input

Validation runs inside `AudioLoader.__init__`, so a missing file or unsupported format raises immediately rather than halfway through a transcription call. This means errors surface at the earliest possible point, close to where the bad input came from, which makes debugging cleaner and avoids wasting API quota on files that were never going to work.

### Explicit format whitelist

`SUPPORTED_FORMATS` is an explicit set based on AssemblyAI's documented supported formats. Checking locally before making a network call gives the user a clear error message instantly and documents the contract of the loader. If AssemblyAI expands their supported formats, updating the pipeline is a one-line change.

### Return the full `Transcript` object

Rather than extracting only the text or only the segments inside `transcribe()`, the function returns the full AssemblyAI `Transcript` object. This keeps downstream flexibility: the caller decides whether they want the raw text, sentence-level segments, word-level timestamps, speaker labels, or any other feature AssemblyAI exposes, without having to modify `transcribe()`.

### Exceptions for error handling

Each failure mode raises a distinct exception type — `FileNotFoundError` for missing files, `ValueError` for unsupported formats, and `RuntimeError` for API failures. 
### Timestamps in milliseconds internally

AssemblyAI returns timestamps in milliseconds, and `get_segments()` preserves that. Conversion to seconds happens only at the display layer, when printing. Keeping internal data in the API's native unit avoids precision loss and makes it obvious when a conversion is happening.


