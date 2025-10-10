# audio9

## Description

Audio9 is an interactive audio learning and playback tool. It allows users to visualize the waveform of audio files (.mp3 or .wav), play the full track, or loop selected sections for detailed listening and practice. Its purpose is to help music enthusiasts, learners, and producers analyze and interact with audio files in a flexible way.

**Key Features:**

* Visual waveform display of audio files
* Play full songs with real-time stopping
* Select and loop specific sections of audio
* Easy-to-use terminal menu for quick control

## Target Audience

* Music learners and students
* Audio enthusiasts
* Music producers and composers
* Anyone wanting to analyze or interact with audio files

## Table of Contents

* [Overview](#overview)
* [How to Run the Program](#how-to-run-the-program)
* [Terminal Menu](#terminal-menu)

  * [Play Full Song](#play-full-song)
  * [Play a Selected Section on Loop](#play-a-selected-section-on-loop)
  * [Quit the Program](#quit-the-program)
* [Screenshot](#screenshot)

## Overview

**Audio Learner by Joseph Moses, Bonsai Entertainment LLC**

Audio9 allows you to interact with audio files by visualizing their waveform and playing or looping specific sections. This makes it easy to practice, analyze, or focus on particular parts of a song.


## How to Run the Program

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the program:

   ```bash
   python3 audio9.py
   ```

A file picker will appear, allowing you to select a .mp3 or .wav file. The audio waveform will then be displayed in a new window.

## Terminal Menu

**Terminal MENU**

Options:

1. Play full song
2. Loop a segment
3. Exit

Select an option (1-3):

### Play Full Song

Press `1` to play the full song.
Click on the waveform window and press `ESC` to stop playback at any time.

### Play a Selected Section on Loop

1. Click and drag on the waveform to select the section you want to loop.
2. The terminal will display the start and stop times of your selection.
3. Press `2` to loop this section, then enter the number of times you want it to repeat.
4. Press `ESC` in the waveform window to stop playback at any time.

### Quit the Program

Press `3` to exit the program. To play a different audio file, restart the script.

## Screenshot

<img width="1646" height="811" alt="audio9" src="https://github.com/user-attachments/assets/6a1e25a3-fbc4-4509-a914-85d22c135fc1" />
