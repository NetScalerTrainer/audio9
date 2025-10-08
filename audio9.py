#!/usr/bin/env python3
# A Python program to play and loop segments of MP3 or WAV audio files on macOS M1
# Uses tkinter for Finder window, waveform display, and Escape key detection,
# and matplotlib for displaying audio waveform with click-and-drag selection and double-click playback
# Requirements: Install pydub, pygame, matplotlib, and ffmpeg
# Run in terminal: pip install pydub pygame matplotlib
# Install ffmpeg via Homebrew: brew install ffmpeg
# tkinter is included with Python on macOS

from pydub import AudioSegment
from pygame import mixer
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import time
import os


class WaveformWindow:
    """Class to manage the persistent waveform window with click-and-drag selection and double-click playback."""
    def __init__(self, audio, file_ext, file_path):
        self.audio = audio
        self.file_ext = file_ext
        self.start_time = None
        self.end_time = None
        self.dragging = False
        self.selection_line = None
        self.is_playing = False
        self.stop_flag = False  # Flag to signal playback stop
        
        self.root = tk.Tk()
        self.root.title("Audio Waveform")
        self.root.geometry("2000x600")
        
        # Bind Escape key to stop playback
        self.root.bind('<Escape>', self.stop_playback)
        
        samples = np.array(audio.get_array_of_samples())
        if audio.channels == 2:
            samples = samples[::2]
        self.sample_rate = audio.frame_rate
        self.duration = len(audio) / 1000
        self.time_array = np.linspace(0, self.duration, len(samples))
        
        self.fig = plt.Figure(figsize=(16, 6))
        self.ax = self.fig.add_subplot(111)
        self.waveform_line, = self.ax.plot(self.time_array, samples, color='blue')
        self.ax.set_title(file_path)
        self.ax.set_xlabel("Time (seconds)")
        self.ax.set_ylabel("Amplitude")
        self.ax.grid(True)
        self.ax.set_xticks(np.arange(0, self.duration + 5, 5))
        self.ax.set_xlim(0, self.duration)
        
        self.fig.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.1)
        self.fig.tight_layout()
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        
        self.root.update()
    
    def stop_playback(self, event):
        """Set the stop flag when Escape key is pressed."""
        if self.is_playing:
            self.stop_flag = True
            print("Escape key pressed. Stopping playback...")

    def on_press(self, event):
        """Handle mouse press to start dragging."""
        if event.inaxes != self.ax or self.is_playing:
            return
        self.dragging = True
        self.start_time = event.xdata
        if self.selection_line is not None:
            self.selection_line.remove()
            self.selection_line = None
        self.canvas.draw()

    def on_motion(self, event):
        """Handle mouse motion to update selection."""
        if not self.dragging or event.inaxes != self.ax or self.is_playing:
            return
        self.end_time = event.xdata
        if self.selection_line is not None:
            self.selection_line.remove()
        self.selection_line, = self.ax.plot([self.start_time, self.end_time], [0, 0], 'r-', linewidth=2)
        self.canvas.draw()

    def on_release(self, event):
        """Handle mouse release to finalize selection or trigger double-click playback."""
        if not self.dragging or event.inaxes != self.ax or self.is_playing:
            return
        self.dragging = False
        self.end_time = event.xdata
        
        if self.start_time and self.end_time:
            self.start_time = max(0, self.start_time)
            if self.start_time > self.end_time:
                self.start_time, self.end_time = self.end_time, self.start_time
            
            if self.selection_line is not None:
                self.selection_line.remove()
            self.selection_line, = self.ax.plot([self.start_time, self.end_time], [0, 0], 'r-', linewidth=3)
            self.canvas.draw()
            
            if abs(self.end_time - self.start_time) <= 0.5:
                print(f"Double-click detected at {self.start_time:.2f} seconds. Playing 5 seconds...")
                end_sec = min(self.duration, self.start_time + 5)
                try:
                    self.play_segment(self.start_time, end_sec, 1)
                except Exception as e:
                    print(f"Error during double-click playback: {e}")
            else:
                print(f"Selected segment: {self.start_time:.2f} to {self.end_time:.2f} seconds")

    def clear_selection_line(self):
        """Clear the selection line from the display."""
        if self.selection_line is not None:
            self.selection_line.remove()
            self.selection_line = None
            self.canvas.draw()

    def play_segment(self, start_sec, end_sec, repeat_count):
        """Play a segment of the audio from start_sec to end_sec, repeated repeat_count times."""
        self.is_playing = True
        self.stop_flag = False
        try:
            start_ms = start_sec * 1000
            end_ms = end_sec * 1000
            if start_ms < 0 or end_ms > len(self.audio) or start_ms >= end_ms:
                raise ValueError(f"Invalid start or end time: start_ms={start_ms}, end_ms={end_ms}, "
                                 f"audio_len={len(self.audio)}")
            
            segment = self.audio[start_ms:end_ms]
            temp_file = f"temp_segment.{self.file_ext}"
            segment.export(temp_file, format=self.file_ext)
            
            if not os.path.exists(temp_file):
                raise FileNotFoundError(f"Temporary file {temp_file} was not created.")
            
            if mixer.get_init():
                mixer.quit()
            mixer.init(frequency=self.audio.frame_rate)
            print(f"mixer initialized with frequency={self.audio.frame_rate}")
            
            mixer.music.load(temp_file)
            print(f"Loaded temporary file: {temp_file}")
            
            for i in range(repeat_count):
                if self.stop_flag:
                    print("Playback stopped by Escape key.")
                    break
                mixer.music.play()
                print(f"Playing repetition {i+1}/{repeat_count} from {start_sec:.2f} to {end_sec:.2f} seconds...")
                
                segment_duration = (end_ms - start_ms) / 1000
                start_time = time.time()
                while mixer.music.get_busy() and time.time() - start_time < segment_duration:
                    if self.stop_flag:
                        print("Playback stopped by Escape key.")
                        mixer.music.stop()
                        break
                    self.keep_alive()
                    time.sleep(0.01)
            
            mixer.music.stop()
            mixer.quit()
            os.remove(temp_file)
        except Exception as e:
            print(f"Error playing segment: {e}")
            if 'temp_file' in locals() and os.path.exists(temp_file):
                os.remove(temp_file)
        finally:
            self.is_playing = False
            self.clear_selection_line()

    def get_selection(self):
        """Return the selected time range (start, end) in seconds."""
        if self.start_time is not None and self.end_time is not None:
            return self.start_time, self.end_time
        return None, None

    def keep_alive(self):
        """Keep the window updated without blocking."""
        try:
            self.root.update()
        except tk.TclError:
            pass


def select_audio_file():
    """Open a Finder window to select an MP3 or WAV file."""
    try:
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Select an MP3 or WAV file",
            filetypes=[("Audio Files", "*.mp3 *.wav")]
        )
        root.destroy()
        if not file_path:
            print("No file selected.")
            return None
        if not (file_path.lower().endswith('.mp3') or file_path.lower().endswith('.wav')):
            print("Error: Only MP3 and WAV files are supported.")
            return None
        return file_path
    except Exception as e:
        print(f"Error selecting file: {e}")
        return None


def load_audio(file_path):
    """Load an audio file and return an AudioSegment object."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError("Audio file not found.")
        audio = AudioSegment.from_file(file_path)
        return audio
    except Exception as e:
        print(f"Error loading audio file: {e}")
        return None


def get_file_extension(file_path):
    """Extract the file extension (mp3 or wav) from the file path."""
    return os.path.splitext(file_path)[1].lower().lstrip('.')


def play_segment(audio, start_sec, end_sec, repeat_count, file_ext):
    """Play a segment of the audio from start_sec to end_sec, repeated repeat_count times."""
    try:
        start_ms = start_sec * 1000
        end_ms = end_sec * 1000
        if start_ms < 0 or end_ms > len(audio) or start_ms >= end_ms:
            raise ValueError(f"Invalid start or end time: start_ms={start_ms}, end_ms={end_ms}, audio_len={len(audio)}")
        
        segment = audio[start_ms:end_ms]
        temp_file = f"temp_segment.{file_ext}"
        segment.export(temp_file, format=file_ext)
        
        if not os.path.exists(temp_file):
            raise FileNotFoundError(f"Temporary file {temp_file} was not created.")
        
        if mixer.get_init():
            mixer.quit()
        mixer.init(frequency=audio.frame_rate)
        print(f"mixer initialized with frequency={audio.frame_rate}")
        
        mixer.music.load(temp_file)
        print(f"Loaded temporary file: {temp_file}")
        
        stop_flag = [False]  # Use a list to modify stop_flag in nested function
        def stop_playback(event):
            stop_flag[0] = True
            print("Escape key pressed. Stopping playback...")
        
        root = tk.Tk()
        root.withdraw()  # Keep window hidden
        root.bind('<Escape>', stop_playback)
        
        for i in range(repeat_count):
            if stop_flag[0]:
                print("Playback stopped by Escape key.")
                break
            mixer.music.play()
            print(f"Playing repetition {i+1}/{repeat_count} from {start_sec:.2f} to {end_sec:.2f} seconds...")
            
            segment_duration = (end_ms - start_ms) / 1000
            start_time = time.time()
            while mixer.music.get_busy() and time.time() - start_time < segment_duration:
                if stop_flag[0]:
                    print("Playback stopped by Escape key.")
                    mixer.music.stop()
                    break
                try:
                    root.update()
                except tk.TclError:
                    break
                time.sleep(0.01)
        
        mixer.music.stop()
        mixer.quit()
        root.destroy()
        os.remove(temp_file)
    except Exception as e:
        print(f"Error playing segment: {e}")
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.remove(temp_file)


def play_full_audio(audio, file_ext):
    """Play the entire audio file."""
    try:
        temp_file = f"temp_full.{file_ext}"
        audio.export(temp_file, format=file_ext)
        if not os.path.exists(temp_file):
            raise FileNotFoundError(f"Temporary file {temp_file} was not created.")
        
        if mixer.get_init():
            mixer.quit()
        mixer.init(frequency=audio.frame_rate)
        print(f"mixer initialized with frequency={audio.frame_rate}")
        
        mixer.music.load(temp_file)
        print(f"Loaded temporary file: {temp_file}")
        
        stop_flag = [False]
        def stop_playback(event):
            stop_flag[0] = True
            print("Escape key pressed. Stopping playback...")
        
        root = tk.Tk()
        root.withdraw()
        root.bind('<Escape>', stop_playback)
        
        mixer.music.play()
        print("Playing full audio (Press Escape to stop)...")
        
        audio_duration = len(audio) / 1000
        start_time = time.time()
        while mixer.music.get_busy() and time.time() - start_time < audio_duration:
            if stop_flag[0]:
                print("Playback stopped by Escape key.")
                mixer.music.stop()
                break
            try:
                root.update()
            except tk.TclError:
                break
            time.sleep(0.01)
        
        mixer.music.stop()
        mixer.quit()
        root.destroy()
        os.remove(temp_file)
    except Exception as e:
        print(f"Error playing full audio: {e}")
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.remove(temp_file)


def main():
    """Main function with command-line interface."""
    print("Audio Segment Looper for Learning Songs")
    file_path = select_audio_file()
    
    if not file_path:
        return
    
    audio = load_audio(file_path)
    if not audio:
        return
    
    file_ext = get_file_extension(file_path)
    
    waveform = WaveformWindow(audio, file_ext, file_path)
    print("Waveform displayed. Double-click to play 5 seconds, click-and-drag to select a segment,"
          " or use manual input.")
    
    while True:
        waveform.keep_alive()
        print("\nOptions:")
        print("1. Play full song")
        print("2. Loop a segment")
        print("3. Exit")
        choice = input("Select an option (1-3): ")
        
        if choice == "1":
            play_full_audio(audio, file_ext)
        elif choice == "2":
            try:
                start_sec, end_sec = waveform.get_selection()
                if start_sec is not None and end_sec is not None:
                    print(f"Using waveform selection: {start_sec:.2f} to {end_sec:.2f} seconds")
                    repeat_count = int(input("Enter number of repetitions (e.g., 5): "))
                    if repeat_count < 1:
                        raise ValueError("Repeat count must be at least 1.")
                    waveform.play_segment(start_sec, end_sec, repeat_count)
                else:
                    start_sec = float(input("Enter start time of segment (seconds): "))
                    end_sec = float(input("Enter end time of segment (seconds): "))
                    repeat_count = int(input("Enter number of repetitions (e.g., 5): "))
                    if repeat_count < 1:
                        raise ValueError("Repeat count must be at least 1.")
                    play_segment(audio, start_sec, end_sec, repeat_count, file_ext)
            except ValueError as e:
                print(f"Invalid input: {e}")
        elif choice == "3":
            print("Exiting program.")
            waveform.root.destroy()
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")


def cleanup_temp_files():
    for temp_file in ["temp_segment.mp3", "temp_segment.wav", "temp_full.mp3", "temp_full.wav"]:
        if os.path.exists(temp_file):
            os.remove(temp_file)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    finally:
        cleanup_temp_files()
      
