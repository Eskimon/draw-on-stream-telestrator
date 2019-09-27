# Draw on stream

This software is designed to help you to easy draw on your stream with tools like OBS Studio or StreamLabs. It is also known as a *telestrator* tool.

## Features

- Hand writing
- Straight line drawing
- Color picker
- Text writing
- Basic shapes (rectangles / circles) filled or not
- Semi-transparent painting scene to see the underlying window

# Usage

## Draw on Stream

You need to have [python installed](https://www.python.org/) on your computer (I might generate a classic .exe some days to simplify windows user's life).

Then, simply start the `painter.py` script. A new window shall appears and you are good to go.

## Adding it OBS

To use Draw on Stream in OBS, add a new "Window Capture" in OBS and select the painter app.
Then, add a filter "Color key" (simpler than "Chroma Key") and set it to your painter background (white is the default).
BOOM, done. You can draw on the painter and it should appear nicely on your stream.

## Shortcut

- `+`: Increment the tool stroke size
- `-`: Decrement the tool stroke size
- `Ctrl +`: Increment the painter window opacity
- `Ctrl -`: Decrement the painter window opacity
- `Ctrl w`: Wipe the current drawing
- `p`: Switch to "pen" mode
- `r`: Switch to "rectangle" mode
- `e`: Switch to "ellipse/circle" mode
- `f`: Toggle the "fill shape" option
