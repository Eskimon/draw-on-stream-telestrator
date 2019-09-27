# Draw on stream

This software is designed to help you to easy draw on your stream with tools like OBS Studio or StreamLabs. It is also known as a *telestrator* tool.

When I started streaming some pedagogical content, I couldn't find any tool to draw on top of my screen.
My requirements were the following:

- The tool should provide an **independant window to capture** (I don't want to capture the full screen and show the world my messy desktop)
- Should be **lightweight**
- Should have plenty of shortcut and **basic drawing tools**
- Must **replace itself** to the same position after each usage
- Should be **free** or cheap

I couldn't find the perfect tool. So I did what every sane person would do: I wrote my own!

So please welcome: ***Draw On Stream*** (or obviously: `DOS`).

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
- `Ctrl z`: Cancel shapes
- `p`: Switch to "pen" mode
- `r`: Switch to "rectangle" mode
- `e`: Switch to "ellipse/circle" mode
- `f`: Toggle the "fill shape" option
- `right-click` to draw straight line

# Extra Notes

The "eraser" does only paint with the foreground color but doesn't really erase the underlying shape.

Also, the source code might look convoluted. Obvisously it's because I change my mind on how to do things in the course of the devlopment. So basically:

- The `painter.py` script can be standalone
- If you want a very transparent painter canvas, it might be difficult to see the buttons. Therefore, you can start the `commander.py` tool. It will send the commands to the `painter` through a socket.
- Any PR is welcomed.

# Wanna thank me?

This tool saved your stream? You wanna thank me? Buy me a beer or some coffee!
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&item_name=
Donation+for+Draw+On+Stream+telestrator&business=WTF33XNRB3XTL&currency_code=EUR&source=url)

Also, you can find me on [Twitter](https://twitter.com/Eskimon_fr), [Twitch](https://twitch.tv/eskimon), or [my very own blog](https://eskimon.fr)!
