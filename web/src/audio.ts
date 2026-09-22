const synth = window.speechSynthesis;
let context: AudioContext | null = null;

// Neither engine starts outside a user gesture, so the first category tap wakes them both.
export function prime() {
  synth.getVoices();
  const warmup = new SpeechSynthesisUtterance(" ");
  warmup.volume = 0;
  synth.speak(warmup);

  context ??= new AudioContext();
  void context.resume();
}

export function play(text: string, slow: boolean): Promise<void> {
  synth.cancel();
  return new Promise((resolve) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = slow ? 0.5 : 1;
    utterance.addEventListener("end", () => resolve());
    utterance.addEventListener("error", () => resolve());
    synth.speak(utterance);
  });
}

export function hush() {
  synth.cancel();
}

export function chime() {
  tone(659.25, 0.16);
  tone(987.77, 0.16, 0.16);
}

export function softTone() {
  tone(349.23, 0.3);
}

export function fanfare() {
  tone(659.25, 0.18);
  tone(783.99, 0.18, 0.16);
  tone(1046.5, 0.5, 0.32);
}

function tone(frequency: number, length: number, delay = 0) {
  if (context === null) return;
  const start = context.currentTime + delay;
  const oscillator = context.createOscillator();
  const gain = context.createGain();

  oscillator.frequency.value = frequency;
  // An exponential ramp cannot reach zero, so it fades to almost nothing instead.
  gain.gain.setValueAtTime(0.0001, start);
  gain.gain.exponentialRampToValueAtTime(0.18, start + 0.02);
  gain.gain.exponentialRampToValueAtTime(0.0001, start + length);

  oscillator.connect(gain).connect(context.destination);
  oscillator.start(start);
  oscillator.stop(start + length);
}
