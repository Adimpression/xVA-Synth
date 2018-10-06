# xVA Synth

xVASynth is an experimental, machine learning based speech synthesis app, using voices from characters/voice sets from Bethesda games.


<img width="100%" src="readme images/github-README.png">


## What this is

This is an Electron UI wrapped around a stripped down version of the original Tacotron (implementation by keithito). The app serves as a framework, which loads and uses whichever models are given to it. As such, the app does nothing by itself, and models need to be installed. Models which have a corresponding asset file will be loaded in its respective game/category. Anything else gets loaded in the "Other" category.


## Why this exists

This has no real purpose yet, to a user, other than just to play around with the voices. At the moment, the quality is not there yet, and until I can get some of the newer models to work, these will not be usable in anything. Some voices had very little amounts of dialogue, and lots is needed for high quality. However, the long term plan is to get to a high enough quality to synthesize new voice acting lines, for new mods (eg. quest mods).

## Installation
The base application can be downloaded and placed anywhere. Aim to install it onto an SSD, if you have the space, to reduce voice set loading time. To install voice sets, you can drop the files into the directory, like you would if manually installing a texture mod. To verify, the files should go in `xVASynth/resources/app/models/<game>/`


## Instructions

To start, double click the xVASynth.exe file, and make sure to click Allow, if Windows asks for permission to run the python server script (this is used internally).


Once the app is up and running, select the voice set category (the game) from the top left dropdown, then click a specific voice set.

A list of already synthesized audio files for that voice set, if any, is displayed. For synthesis, click the `Load model` button. This may take a minute, on a slow machine.

Once finished, type your text in the text area and click the `Generate Voice` button. Once generated, you will be shown a preview of the output. Click the `Keep sample` button to save to file, or click the `Generate Voice` after making ammends to the text input, to discard it and re-generate.

In the below list of audio files, you can preview, click to open the containing folder, or delete each one.

**Note about synthesis quality**

Given the very small amount of data used in training, the somewhat outdated synthesis code, the output is mediocre at best, and outright terrible at other times. Proper sentences can be still be created with trial and error.

The best approach I have found is to generate samples of at least 2 seconds in length, and not much more than 5. If you need a lot of text to be synthesized, the current best approach is to synthesize smaller clauses, and splicing them together in Audacity. If you need something really short, and it can't synthesize it, you can add a small sentence (EG `Some stuff.`) before and/or after your text, and cutting it out in Audacity.

All models have also been trained on my personal machine, with a GTX 1080, meaning that `batch_size` had to be limited, to stay within memory constraints. With any luck, I may get access to some beefier machines in the future to train models with better attention.

## Pro tips:

- Right click a voice set in the left bar to hear a sample of the voice.

- To change pronounciation, you can change spelling (cmudict is supported for models that were trained with it)

- You can use full stops and commas to change timing

- Try doing multiple takes, using different spellings, punctuation and input lengths.

- A model's first synthesis takes the longest. Subsequent ones are faster due to caching.

- Acronyms should be spelled out phonetically. EG: xVA -> Ex vee ay

- Numbers automatically get converted to text. However, if you need to pronounce years, such as 1990 -> nineteen ninety, instead of one thousand nine hundred and ninety, you should split the two numbers, like 19 90.

## Development

`npm install` dependencies, and run with `npm start`. Use virtualenv, and `pip install -r requirements.txt` using Python 3.6.

The app uses both JavaScript (Electron, UI) and Python code (Tacotron Model). As the python script needs to remain running alongside the app, and receive input, communication is done via an HTTP server, with the JavaScript code sending localhost requests, at port 8008. During development, the python source is used. In production, the compiled python is used.

## Packaging

Use pyinstaller to compile the python, and run the scripts in `package.json` to create the electron distributables.

## Models

The existing models have been trained on roughly 500k steps, each, at roughly 10 outputs_per_step, with batch_size of 16 or 24 (in order to be able to fit everything on 8GB of VRAM).

Currently, the following voices/characters have been trained:

### Skyrim:

<ul>
    <li>Female Even Toned</li>
    <li>Male Dunmer</li>
    <li>Male Soldier</li>
    <li>Male Elf Haughty</li>
    <li>Sheogorath</li>
    <li>Delphine</li>
</ul>

### Oblivion:
<ul>
    <li>Male Breton</li>
    <li>Uriel Septim</li>
    <li>Male Imperial</li>
</ul>

### Morrowind:
<ul>
    <li>Male Bretons and Orcs</li>
</ul>

### Fallout 3:
<ul>
    <li>Narrator</li>
    <li>Mr Burke</li>
</ul>

### Fallout 4:
<ul>
    <li>Nora (needs re-training)</li>
    <li>Nate</li>
</ul>

### Fallout New Vegas:
<ul>
    <li>Joshua Graham</li>
    <li>FemaleAdult04 (needs re-training)</li>
    <li>Narrator</li>
</ul>

Some of these share the same model, due to having the same voice actor, across games.

## Future Plans

### App
This is an just early experiment. The quality of the voice files currently leaves to be desired, due to the low amount of data available. As technology improves, time permitting, the core synthesis algorithms will get updates, and if necessary, models retrained.

Training a specific voice set takes about 6-7 days, on average, depending on the hyper-parameters used. In total, about 4 months went into getting the first list of voices trained. However, about 90% of the time/work that went into this went into collecting, aligning, and pre-processing the audio files. When trying out newer models, things should move along a bit faster, as the data has already been put together.

The app is capable of using CMUDict for the models that have been trained with it. So far, however, the models that I have trained with support for it have been of lower quality. However, if trained with with support for it, CMUDict syntax can be used in the input textarea.

### Models

Models are being trained for the following games:

- The Elder Scrolls V: Skyrim
- The Elder Scrolls IV: Oblivion
- The Elder Scrolls III: Morrowind
- Fallout 3
- Fallout 4
- Fallout New Vegas

Time/interest/data permitting, other games/categories may be explored.

## Contribute

This project is the first time I've explored neural voice synthesis, so if you have more experience than me, and/or think you can contribute in any way, don't hesitate to contact me, or open an issue!

## Credits

Models are trained, and evaluation is done using code from keithito's implementation of Tacotron: https://github.com/keithito/tacotron