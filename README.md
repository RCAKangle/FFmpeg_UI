# FFmpeg GUI

A small Tkinter desktop tool that wraps common ffmpeg workflows with a simple GUI.

## Features
- Split video into image frames
- Merge image frames into a video (configurable frame rate)
- Transcode video (codec chosen by output format)
- Reverse video (video + audio)
- Extract audio stream

## Requirements
- Python 3.x
- ffmpeg available on PATH  
  Verify with `ffmpeg -version`

## Run
```bash
python main.py
```

## Usage Notes
- Split: output frames are named `frame_%05d.png`.
- Merge:
  - Select a directory that contains the frame images.
  - The app renames frames to `00001.ext` style before merging.
  - All frames must share the same extension (png/jpg/jpeg).
- Transcode:
  - `.mp4` -> `libx264`
  - `.avi` -> `libxvid`
  - others -> `libx265`
- Extract audio uses `-acodec copy`; choose an extension compatible with the source audio.

## Prebuilt App
A ready-to-run executable is available at `dist/main.exe`.

## Notes
- Merging will rename all frames in the selected folder. Keep only the intended frames there.
- ffmpeg errors are shown in a dialog.
