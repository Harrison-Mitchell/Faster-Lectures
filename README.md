# Faster Lectures
Using a conglomerate of cutting edge technology, trim down the length of time university lectures take to digest. Reach improvments of anywhere between 10-15x

### Abstract
Takes a video lecture file, removes coughs, sneezes, silences, "umm"'s etc... Applies some machine learning to grab only the vital moments in the lecture and returns a lecture with all pertinent information retained, only difference being that it's up to 10x faster to consume.

### Dependencies
* [Extract Lecture Slides.py](https://github.com/Harrison-Mitchell/Extract-Lecture-Slides) (Requires: `pip3 install img2pdf opencv-python numpy`)
* [jumpCutter.py](https://github.com/carykh/jumpcutter) (Requires: `pip3 install Pillow audiotsm scipy numpy pytube`)
* Google Cloud + GCSpeech (`pip3 install google-cloud google-cloud-speech`)
* OS with BASH (although feel free to translate)
* FFMPEG (`apt install ffmpeg`)
* Python >= 3.5

### Foreword
This project was originally a thought I had sitting through boring lectures. Then it became a extravagant joke for [this video](https://www.youtube.com/watch?v=nbqitGDctgU) I made to be shared with mates. Finally it became an idea with some merit behind it which is why I decided to throw it up on here, because I use it weekly. If you've got a few minutes, I ask that you give the original video a shot because a lot of what's to come will make far more sense. This project has turned many of my 2 hour lectures into 14 minute ones without losing information, [although...](https://xkcd.com/1319/)

<div align="center">
  <a align="center" href="https://www.youtube.com/watch?v=nbqitGDctgU"><img align="center" src="https://img.youtube.com/vi/nbqitGDctgU/0.jpg" width="300px"></a>
</div>

### Removing Silence, Coughs, "Umm"s and "Uhh"s
Was going to write this myself but carykh was already all over it, [here](https://github.com/carykh/jumpcutter)'s the project and [here](https://www.youtube.com/watch?v=DQ8orIurGxw)'s a entertaining video carykh's made on the script. Script does ok on longer videos but where it really falls apart is when your OS cries about a directory having over 300,000 items. So we grab our lecture video, split it into 30min segments, remove the silences and join the processed segments back into one video. (You may need to play with `--silent_threshold`)
```
ffmpeg -nostats -loglevel 0 -i input.mp4 -c copy -map 0 -segment_time 1800 -f segment split%1d.mp4
for vid in split*.mp4; do python3 jumpcutter.py --input_file $vid --silent_speed 999999 --frame_margin 2; done
for cut in *_ALTERED.mp4; do echo file $cut; done > cuts.txt
ffmpeg -nostats -loglevel 0 -f concat -i cuts.txt -c copy cutInput.mp4
```

### Transcribing the Lecture to be Read
[ZapReader](https://www.zapreader.com/) allows you to read text super fast, I can do 500wpm comfortably. The average speaking speed is 150wpm. Current speech transcription is pathetic, I'm sorry, but NLP is only fairly recent and still needs a lot of work, that being said, it's not awful... As Google trains on more samples, their models will get better, so it's a matter of time. So here we make a mono .wav file which we then (**manually**) upload to a GCP bucket. Throw that GCP bucket link into the first line of the STT file and give it about (audio length / 3) to transcribe. Once done, feed `trans.txt` into [ZapReader](https://www.zapreader.com/).
```
ffmpeg -nostats -loglevel 0 -i input.mp4 -ac 1 input.wav
# Upload to GCP bucket and edit STT file line 1
export GOOGLE_APPLICATION_CREDENTIALS="key.json"
wget https://raw.githubusercontent.com/Harrison-Mitchell/Faster-Lectures/master/STT.py
python3 STT.py > trans.txt
```

### Condense Transcript to Important Parts only
Using NLP and various other statistical operations, formulate sentences that best summarize a section of the transcription. This removes sentences that reiterate an idea, aren't relevant to the information such as "what have I done wrong here?", or are just trivialities such as "Good morning everyone" which is why I can claim that I'm not losing any necessary information. You'll need to apply for a free API key at [SMMRY](https://smmry.com/) which takes care of the dirty work for us. Strangely you can only specify the number of output sentences you want, not percentage of original text or anything. So we'll go for the maximum of 40 returned sentences and send it 100 sentences at a time. Just looking at some transcripts, there are many "sentences" that are just "Okay." and "Hello." etc. Blindly assuming these are 10% of sentences, my aim in throwing 100 sentences to get 40 back is that the meat of the content is reduced by half. I.e keep the more important half of the transcript. So we'll split our transcript into sections of 100 lines, send each split to the API, decode the returned JSON and combine all API responses into one file to get our condensed transcription that's hopefully half the size!
```
SPLITS=$(echo $(cat trans.txt | wc -l) / 100 + 1 | bc)
split -da 4 -n r/$SPLITS trans.txt transSplit --additional-suffix=".txt"
for split in transSplit*.txt
  do curl -F "sm_api_input=$(cat $split)" -X POST "http://api.smmry.com/&SM_API_KEY=<APIKEY>&SM_LENGTH=40" | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['sm_api_content'])" >> shortTrans.txt; done
```

### Extract Slides
I would hope the meat of a lecture is in the words, not the slides. But I'd argue they're still worth the glace. So I wrote a tool to scrape the slides from a lecture if the slides aren't released separately [here](https://github.com/Harrison-Mitchell/Extract-Lecture-Slides). You feed it the video and it returns a slideshow PDF.

### Future Work
To go full circle, the condensed transcript could then be fed into a CNN trained on the lecturers voice so we get returned a video with the lecturer "presenting" their lecture far more efficiently and resyncing the slide show. Perhaps go as far as to market the resulting videos to the students who leave their lectures until the final exam.
> Have 24 hours worth of lectures to catch up on? Get them out of the way in only 5 hours! Just $10 :)

### Legality
You're responsible for knowing whether you're allowed to download/keep a local copy of the lecture video or extract a lecturer's slideshow since they're usually copyright by default. Now, I'm not endorsing going around these restrictions... but you'll have my respect for caring about your learning!
