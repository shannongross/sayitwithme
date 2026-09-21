# Say It With Me

Practice saying English phrases out loud, without needing to read anything.

Live demo: [sayitwithme.pages.dev](https://sayitwithme.pages.dev). Works best on a phone.

The motivation for this app was a Rohingya refugee family that resettled near me. I spent
time teaching the mother English, and we ran into a wall quickly. Rohingya is primarily an
oral language, with no widely used written form, so Google Translate and similar tools were
of no help. Most adult English resources, Duolingo included, assume the learner can read in
some language, and oral-only English lessons, particularly for Rohingya speakers, are
virtually nonexistent.

This app is for adults who want to learn spoken English without relying on any written
language. Nothing on screen is text; every control is a picture, a sound or a color. Work is
ongoing to collect audio from Rohingya volunteer translators so learners can hear each phrase
in their own language first.

## How it works

The learner taps a picture, hears the phrase, and records an attempt. The recording is sent
to the API, where an LLM transcribes it to text. A deterministic grader then compares that
transcription against the key words of the target phrase; the attempt passes when every key
word is present. The API returns "understood" or "not yet", deletes the recording, and the
phone shows the result as a color, an icon and a sound.

The frontend is React, the API is Python, and content lives in Postgres, all hosted on
Google Cloud. Pictures come from an AAC symbol library.

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
