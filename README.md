# Say It With Me

Practice saying English phrases out loud, without needing to read anything.

Live demo: [sayitwithme.pages.dev](https://sayitwithme.pages.dev). Works best on a phone.

I built this for a Rohingya family who were resettled near me. The adults had never been to
school and do not read in any language, including their own, which is mostly a spoken one.
They wanted enough English to get through a clinic visit or a bus ride on their own. Every
app I tried with them assumed you could read, if not English then at least the menus in your
first language. None of them worked for people who can't read at all.

This app has no text on screen. The learner taps a picture, hears the phrase, repeats it, and
receives a green check or an amber "try again".

## How it works

The phone records a short attempt and sends it to the API. The API transcribes it with a
speech-to-text model, checks that the content words of the target phrase are present, and
returns "understood" or "not yet". The recording is deleted before the response is sent. All
feedback on the phone is color, icon and sound.

The stack is a React frontend, a Python API and Postgres, hosted on Google Cloud. Pictures
come from an AAC symbol library, and every learner hears the same English voice.

## Choices that shaped it

**The pictures are AAC symbols.** AAC (augmentative and alternative communication) is the
field of tools for people who can't rely on speech or text, and its symbol libraries are large
sets of simple pictograms, one per word or idea, with a consistent style and a plain label on
each.

**Rohingya audio will come from Rohingya speakers.** The plan is for volunteers to record
each phrase in their own language so a learner can hear the meaning first.

**It grades intelligibility, not accuracy.** The grader strips function words from the target
phrase and checks that the content words were said, so "I need interpreter" passes. A false
rejection discourages exactly the learner this is built for, so the threshold is deliberately
lenient.

**User voice isn't kept.** No accounts, no saved recordings, no stored transcripts. A hosted
transcription service hears the audio, evaluates performance, and discards recording.


## Licensing

The code is MIT. The pictograms in `content/media/img` are not: they come from
[Global Symbols](https://globalsymbols.com) under CC BY-SA 4.0, and `content/media/MANIFEST.csv`
records the source, symbol set and license of every file. Credit Global Symbols if you reuse
them, and share any modified pictogram under the same license.
