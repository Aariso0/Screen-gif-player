# Borderless Animation Player

A tiny Windows desktop animation player for running your own GIF or frame animation as a borderless, draggable, always-on-top widget.

This is built to recreate the practical **AnimaEngine-style GIF playing feature**: drop in an animation, run the player, and have it sit on your desktop without a normal window border. It does not include AnimaEngine code, branding, or bundled assets.

## What It Does

- Plays an animated GIF, PNG, or folder of image frames.
- Runs as a borderless desktop widget.
- Supports transparent backgrounds.
- Can stay always on top.
- Can be dragged around with the mouse.
- Has right-click controls for pause, reload, size, and exit.
- Supports screen-size presets: 25%, 20%, 15%, 10%, and 5%.
- Can optionally use click-through mode so mouse clicks pass through the animation.

## Install

1. Install Python for Windows:

   [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)

2. During Python installation, enable:

   ```text
   Add python.exe to PATH
   ```

3. Download or copy this project folder to your PC.

4. Put your animation file here:

   ```text
   animations/
   ```
and Name it

```text
animation.gif
```
if you have any other format like an png use animation.your_format

   The file can be a real GIF, a PNG, or a folder of frames. If you use a different name, update `animation_config.json`.

5. Double-click:

   ```text
   run_borderless_animation.bat
   ```

IF you use .bat file you can freeley drag your gif out of the black window.

If you don't want the black window open terminal to the git folder location and then run

```text
python ./borderless_animation_player.py
```

## Configure

Edit `animation_config.json`:

```json
{
  "animation": "animations/diane.gif",
  "frame_delay_ms": 80,
  "scale": 1.0,
  "screen_percent": 15,
  "transparent_color": "#010203",
  "always_on_top": true,
  "click_through": false,
  "start_x": 120,
  "start_y": 120
}
```

Common settings:

- `animation`: path to your GIF, PNG, or frame folder.
- `frame_delay_ms`: animation speed. Lower is faster.
- `screen_percent`: widget size based on your screen. Use `25`, `20`, `15`, `10`, or `5`.
- `transparent_color`: color that becomes invisible.
- `always_on_top`: keeps the animation above other windows.
- `click_through`: lets mouse clicks pass through the widget.
- `start_x` and `start_y`: starting position on screen.

## Controls

- Left-click and drag: move the animation.
- Right-click: open the control menu.
- Space: pause or resume.
- Escape: close.

## Transparency Notes

If your GIF or PNG has real transparency, it should work normally.

If your animation has a solid background, set that background to the same color as `transparent_color`. The default transparent color is:

```text
#010203
```

## Click-Through Warning

When `click_through` is `true`, you cannot drag or right-click the widget because mouse input passes through it.

To change it back, close the player and edit:

```json
"click_through": false
```

## Project Files

- `borderless_animation_player.py`: main app.
- `animation_config.json`: user settings.
- `run_borderless_animation.bat`: Windows launcher.
- `animations/`: place your animation files here.

## Notes

This project is meant for the GIF/animation-widget part of an AnimaEngine-like workflow. It is not a full wallpaper engine, Steam Workshop client, or native Windows wallpaper setter.
