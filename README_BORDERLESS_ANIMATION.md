# Borderless Animation Player

This runs your own animation as a transparent, borderless desktop widget.

you can basicaley replicate that one feature of animaengine where you can have animations running on your desktop

## Quick Start

1. Put your gif animation here:

```text
animations/
```

2. Name it

```text
animation.gif
```
if you have any other format like an png use animation.your_format

3. Double-click:

```text
run_borderless_animation.bat
```

OR you can just use 

```text
python ./borderless_animation_player.py
```

## Supported Inputs

- Animated `.gif`
- A folder of `.png` or `.gif` frames
- Single `.png` or `.gif`

To use a frame folder, edit `animation_config.json`:

```json
{
  "animation": "animations/my_frames",
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

## Controls

- Drag with left mouse button
- Right-click for pause, reload, screen-size options, and exit
- Space pauses/resumes
- Escape closes

## Size Options

Set `screen_percent` in `animation_config.json` to one of these values:

```text
25, 20, 15, 10, 5
```

This sizes the animation using the smaller side of your screen. Remove `screen_percent` or set it to `null` if you want to use raw `scale` instead.

## Transparency

For GIFs and PNG frames with real alpha transparency, it should just work.

For animations without alpha, set the background color in your frames to the same value as `transparent_color`, currently `#010203`.

## Click-Through Mode

Set `"click_through": true` if you want mouse clicks to pass through the animation.

Important: when click-through is enabled, you cannot drag or right-click the widget. Use Escape while it is focused, Task Manager, or set it back to false in the config before launching again.

## Setup auto start up

This app is still under development I will add the auto start up feature once I have all the feature that I want .

for now you can just use windows features to setup an auto startup for this it won't be perfect but it will do the job .
