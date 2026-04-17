# Import basic preliminaries
import wave

from sic_framework import AudioRequest
from sic_framework.core.sic_application import SICApplication
from sic_framework.core import sic_logging
from sic_framework.devices.common_desktop.desktop_speakers import SpeakersConf

# Import the device we will be using
from sic_framework.devices.desktop import Desktop

class SpeakerTest(SICApplication):
    """
    Desktop camera demo application.
    """

    def __init__(self):
        # Call parent constructor (handles singleton initialization)
        super(SpeakerTest, self).__init__()

        # Configure logging
        self.set_log_level(sic_logging.INFO)
        self.desktop = None
        self.speaker = None

        # Log files will only be written if set_log_file is called. Must be a valid full path to a directory.
        # self.set_log_file("/Users/apple/Desktop/SAIL/SIC_Development/sic_applications/demoss/desktop/logs")

        self.setup()


    def setup(self):
        self.desktop = Desktop(speakers_conf=SpeakersConf(sample_rate=22050))
        self.speaker = self.desktop.speakers

    def play_audio(self, audio_file, block=True):
        with wave.open(audio_file, 'rb') as wf:
            # Get parameters
            sample_width = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()

            # Ensure format is 16-bit (2 bytes per sample)
            if sample_width != 2:
                raise ValueError("WAV file is not 16-bit audio. Sample width = {} bytes.".format(sample_width))

            self.speaker.request(AudioRequest(wf.readframes(n_frames), framerate), block=block)

    def run(self):
        self.play_audio('tts_cache/1a/1ad328dd8a9fea4ec50f0c8a4e737e53.wav', block=False)
        self.play_audio('tts_cache/3c/3c528cbf967c043be849a59fa4cb5958.wav')


if __name__ == "__main__":
    # Create and run the demo
    # This will be the single SICApplication instance for the process
    demo = SpeakerTest()
    demo.run()
