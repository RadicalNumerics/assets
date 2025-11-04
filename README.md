# Radical Numerics Assets



This repository contains the assets (such as svg, png, etc.) for Radical Numerics. 


## SVGs

SVGs are meant to be easy to use, lightweight, and easy to modify -- this includes smooth vector animations without the need for wasteful GIFs!


### Development

We recommend using Cursor/VSCode to edit them, which allows to use agents to edit them:

1. Install the [SVG extension by jock](https://marketplace.cursorapi.com/items/?itemName=jock.svg): go to Extensions -> Search for "SVG" -> Install the extension by jock.
2. Open the SVG file in with a text editor (right click -> Open with -> text editor). You can also set the text editor as default for `*.svg` files.
3. Right click on the SVG file -> Preview SVG. This way you can edit the code and see the result in real time as in the below screenshot:

![SVG Preview](./png/screenshots/workflow-svg.png)


Example vectorized logo:

<p align="center">
  <img width=500 alt="Spear Logo" src="svg/rn-logo-desktop-vector.svg" />
</p>

Example animation:

<p align="center">
  <img width=500 alt="Spear Logo" src="svg/rn-logo-desktop-vector-animated.svg" />
</p>


### Tips and tricks

- Add automatic switching between light and dark mode:

```html
<style>
:root {
    --main-color: #0c0c0c;
    }
    @media (prefers-color-scheme: dark) {
    :root { --main-color: #ffffff; }
    }
</style>
```

> Also, unlike FlashInfer and vLLM that use separate png logos for light and dark mode (150+kb), we can use a single svg in <10kb!


## Braille⠸⠱

The logo can be roughly reproduced in 2 braille characters -- noting that each braille character is made up of 8 dots in a 4x2 grid and we selectively choose which dots to include. The upright version is any of the following: `⠏⠆`, `⠸⠱`, `⡖⡄` or `⢰⢢` , which can be easily copied and pasted. 

For fancier versions, you can use the `braille_logo.py` for transformations:

```bash
python scripts/braille_logo.py --frames "⠏⠆" --move DR --rotate 90 # output: ⣒⠆
```