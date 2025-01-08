import pyaudio
import numpy as np
import aubio
import keyboard
import pygetwindow as gw
from ahk import AHK
ahk = AHK(executable_path='C:\Program Files\AutoHotkey\AutoHotkeyV2.exe')

# Aubio parameters and stuff (ngl idk what they mean)
RATE = 44100
CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1

p = pyaudio.PyAudio()

# Change the audio input to whatever device you're using
print("Available audio input devices:")
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f"{i}: {info['name']}")

input_device_index = 1 # Right here

current_device_info = p.get_device_info_by_index(input_device_index)
print(f"Using audio device: " + current_device_info['name'])

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=input_device_index,
                frames_per_buffer=CHUNK)

pitch_detector = aubio.pitch("yin", CHUNK)
pitch_detector.set_unit("Hz")

# A list of frequencies corresponding to each fret on the high e string
def get_key_for_pitch(pitch): # Might need to adjust values for frequencies
    key_freq = {
        (320, 340): "click",
        (340, 360): "left",
        (360, 380): "right",
        (380, 400): "w+space",
        (400, 420): "1",
        (420, 450): "2",
        (450, 470): "3",
        (470, 500): "4",
        (500, 530): "click",
        (530, 600): "g"
    }   
    
    for freq_range, key in key_freq.items():
        if freq_range[0] <= pitch < freq_range[1]:
            return key
    return None

try:
    roblox_window = None
    for window in gw.getWindowsWithTitle('Roblox'):
        if 'Roblox' in window.title:
            roblox_window = window
            break
    
    # Focuses the window (completely unnecessary but after it started working I just didn't touch it)
    if roblox_window:
        roblox_window.activate()
    else:
        print("Cannot find Roblox window")
    
    last_key = None

    def releaseLastKey():
        ahk.key_release(last_key)
        print("Released " + last_key)

        if last_key == "w+space":
            ahk.key_release("space")
            ahk.key_release("w")
        if pitch_key == "w+shift":
            ahk.key_release("shift")
            ahk.key_release("w")

    while True:
        # More Aubio stuff that I'm not qualified to give my explanation for
        data = stream.read(CHUNK, exception_on_overflow = False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        audio_data = audio_data.astype(np.float32) / 32768.0
        audio_data = audio_data.copy()

        # Detect pitch using Aubio
        pitch = pitch_detector(audio_data)
        pitch_value = pitch[0]
        
        # print(pitch_value)

        if pitch > 0 and pitch < 1000:
            pitch_int = round(pitch_value)
            pitch_key = get_key_for_pitch(pitch_int)
            # print(pitch_int)

            # If the pitch corresponds to a key
            if pitch_key != None:
                # Print the corresponding key to the pitch
                # print(pitch_key)
                
                # If the last key doesn't equal to new key
                if last_key != pitch_key:
                    if last_key != None: # Release the last key if it exists
                        releaseLastKey()

                    # Press down the new key
                    ahk.key_down(pitch_key)
                    print("Pressed " + pitch_key)
                    
                    # Very improvised double key input stuff - Feel free to change
                    if pitch_key == "w+space":
                        ahk.key_down("space")
                        ahk.key_down("w")
                    if pitch_key == "w+shift":
                        ahk.key_down("shift")
                        ahk.key_down("w")
                    if pitch_key == "click":
                        ahk.click()

                    last_key = pitch_key
            else:
                # If the new key doesn't exist and the last key does exist, then release the last key
                if last_key != None:
                    releaseLastKey()
                    last_key = None
        else:
            # If the new pitch is outside the limits, then if theres a last_key, release it
            if last_key != None:
                releaseLastKey()
                last_key = None
