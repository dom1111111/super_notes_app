"""
Two classes that uses the Pyaduio module to start, pause, and stop audio playing and recording!

* Instantiate with `PlayAudio` for playing, 
* `RecAudio` for recording
"""

import pyaudio
import wave

class PlayAudio:
    """
    Functions:
    * `play(audio_file_path)` - play audio in a seperate thread
    * `pause_toggle()` - pause and resume audio playing
    * `stop()` - ends the audio playing
    * `terminate()` - call this when you no longer want to use this
    """
    def __init__(self):
        self.p = pyaudio.PyAudio()     # instantiate PyAudio
        # possible_states = 'off', 'playing', 'paused'
        self.state = 'off'

    # play audio based on audio file path provided
    def play(self, audio_file_path: str):
        # if the current stream is active, stop it first, then play
        if self.state == 'playing':
            self.stop()

        file = wave.open(audio_file_path, 'rb')

        def callback(in_data, frame_count, time_info, status):
            data = file.readframes(frame_count)
            return (data, pyaudio.paContinue)

        # open stream with PyAudio-instance's open()
        self.stream = self.p.open(
            format = self.p.get_format_from_width(file.getsampwidth()),
            channels = file.getnchannels(),
            rate = file.getframerate(),
            output = True,                  # 'Specifies whether this is an output stream. Defaults to False.'
            stream_callback = callback
            )

        self.stream.start_stream()
        self.state = 'playing'

    # pause or resume audio stream
    def pause_toggle(self):
        if hasattr(self, 'stream'):             # first checks if 'stream' exists (it won't exist if nothing was played yet)
            if self.state == 'playing':
                self.stream.stop_stream()       # pauses the stream
                self.state = 'paused'
            elif self.state == 'paused':
                self.stream.start_stream()      # resumes the stream
                self.state = 'playing'

    # close the audio stream
    def stop(self):
        if hasattr(self, 'stream'):
            self.stream.close()                 # closes the stream
            self.state = 'off'
    
    def terminate(self):
        self.p.terminate()                      # closes the instance of pyaudio


class RecAudio:
    """
    Functions
        * `record()` - start a recording in a sperate thread
        * `stop_and_return()` - ends the audio recording and returns the raw audio data
        * `write_to_file(audio, file_path)` - takes in audio data and writes it to a wave file accroding to the file path given
        * `terminate()` - call this when you no longer want to use this
    """
    def __init__(self):
        self.p = pyaudio.PyAudio()     # instantiate PyAudio
        # possible_states = 'off', 'recording', 'paused'
        self.state = 'off'

        self.CHUNK = 1024                # https://dsp.stackexchange.com/questions/13728/what-are-chunks-when-recording-a-voice-signal
        self.FORMAT = pyaudio.paInt16    # https://people.csail.mit.edu/hubert/pyaudio/docs/#pasampleformat
        self.CHANNELS = 1
        self.RATE = 44100
    
    # record audio from default recording device
    def record(self):
        if not self.state == "recording":
            CHUNK = self.CHUNK  
            FORMAT = self.FORMAT
            CHANNELS = self.CHANNELS
            RATE = self.RATE

            self.audio_frames = []

            def callback(in_data, frame_count, time_info, status):
                self.audio_frames.append(in_data)
                return (in_data, pyaudio.paContinue)

            self.stream = self.p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                stream_callback=callback
                )

    # close the audio stream and return audio data
    def stop_and_return(self):
        if hasattr(self, 'stream'):
            self.stream.close()                 # closes the stream
            self.state = 'off'
            audio_data = b''.join(self.audio_frames)    # the b''.join is to join the bytes/chunks together in a single thing
            # audio_data = self.audio_frames
            self.audio_frames.clear()           # reset the frames list to be empty for the next audio
            return audio_data
    
    # takes the raw audio data and writes it to a wav file
    def write_to_file(self, audio_data, file_path: str):
        FORMAT = self.FORMAT
        CHANNELS = self.CHANNELS
        RATE = self.RATE

        sample_width  = self.p.get_sample_size(FORMAT)

        with wave.open(file_path, 'wb') as file:
            file.setnchannels(CHANNELS)
            file.setsampwidth(sample_width)
            file.setframerate(RATE)
            file.writeframes(audio_data)
            file.close()

    def terminate(self):
        self.p.terminate()                      # closes the instance of pyaudio
