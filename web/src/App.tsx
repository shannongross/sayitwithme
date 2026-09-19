import { useEffect, useRef, useState } from "react";


type Lesson = {
  image_url: string;
  phrase: {
    id: string;
    text: string;
  };
};

type Screen = "start" | "home" | "lesson";
type Result = "understood" | "not_yet" | null;


function speak(text: string, slow = false) {
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = slow ? 0.65 : 0.9;
  window.speechSynthesis.speak(utterance);
}

function audioType() {
  if (MediaRecorder.isTypeSupported("audio/webm;codecs=opus")) {
    return "audio/webm;codecs=opus";
  }
  return "audio/mp4";
}

export default function App() {
  const [screen, setScreen] = useState<Screen>("start");
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [recording, setRecording] = useState(false);
  const [result, setResult] = useState<Result>(null);
  const recorder = useRef<MediaRecorder | null>(null);
  const timer = useRef<number | null>(null);

  useEffect(() => {
    fetch("/api/lesson")
      .then((response) => response.json())
      .then(setLesson);
  }, []);

  useEffect(() => {
    if (screen === "lesson" && lesson) {
      speak(lesson.phrase.text, true);
    }
  }, [screen, lesson]);

  function begin() {
    window.speechSynthesis.getVoices();
    setScreen("home");
  }

  async function toggleRecording() {
    if (recording) {
      recorder.current?.stop();
      return;
    }

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const nextRecorder = new MediaRecorder(stream, { mimeType: audioType() });
    const parts: BlobPart[] = [];
    nextRecorder.addEventListener("dataavailable", (event) => parts.push(event.data));
    nextRecorder.addEventListener("stop", async () => {
      stream.getTracks().forEach((track) => track.stop());
      if (timer.current) window.clearTimeout(timer.current);
      setRecording(false);
      await submit(new Blob(parts, { type: nextRecorder.mimeType }));
    });
    nextRecorder.start();
    recorder.current = nextRecorder;
    setResult(null);
    setRecording(true);
    timer.current = window.setTimeout(() => nextRecorder.stop(), 8_000);
  }

  async function submit(audio: Blob) {
    if (!lesson) return;
    const form = new FormData();
    form.append("phrase_id", lesson.phrase.id);
    form.append("audio", audio, "attempt.webm");
    const response = await fetch("/api/attempts", { method: "POST", body: form });
    const attempt = await response.json();
    setResult(attempt.result);
    if (attempt.result === "not_yet") speak(lesson.phrase.text, true);
  }

  if (screen === "start") {
    return <button className="start" aria-label="Start" onClick={begin}>▶</button>;
  }

  if (!lesson) return null;

  if (screen === "home") {
    return (
      <main className="home">
        <button className="lesson" aria-label="Clinic" onClick={() => setScreen("lesson")}>
          <img src={lesson.image_url} alt="" />
        </button>
      </main>
    );
  }

  return (
    <main className="card">
      <img className="scene" src={lesson.image_url} alt="" />
      {result && <div className={`result ${result}`} role="status">{result === "understood" ? "✓" : "↻"}</div>}
      <div className="controls">
        <button aria-label="Hear phrase" onClick={() => speak(lesson.phrase.text)}>▶</button>
        <button aria-label="Hear slowly" onClick={() => speak(lesson.phrase.text, true)}>◷</button>
        <button className={recording ? "recording" : ""} aria-label="Record" onClick={toggleRecording}>●</button>
        <button aria-label="Home" onClick={() => setScreen("home")}>⌂</button>
      </div>
    </main>
  );
}