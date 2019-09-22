STORAGE_URI = 'gs://REPLACE/ME.wav'

from google.cloud import speech_v1
from google.cloud.speech_v1 import enums

transcript = ""
client = speech_v1.SpeechClient()
config = {"language_code": "en-AU", "enable_automatic_punctuation": True}
audio = {"uri": STORAGE_URI}
operation = client.long_running_recognize(config, audio)

for result in operation.result().results:
	transcript += str(result.alternatives[0].transcript)
	
# Will become apparent later
transcript = transcript.replace("\n", " ").replace("\r", " ").replace("\"", "'")
transcript = transcript.replace("  ", " ").replace("  ", " ").replace(".", ".\n")
print(transcript)
