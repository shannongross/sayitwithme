import { useCallback, useEffect, useRef, useState, type CSSProperties } from "react";

import { base, postAttempt, type Outcome, type Phrase } from "./api";
import { chime, hush, play, softTone } from "./audio";
import { Arrow, Bars, Check, Grid, Loop, Mic, Play, Turtle } from "./icons";
import { limit, record, type Recording } from "./recorder";

type Status =
  | { kind: "playing"; slow: boolean }
  | { kind: "ready" }
  | { kind: "recording" }
  | { kind: "result"; outcome: Outcome };

const pause = 1_400;

export default function Practice({
  phrases,
  onExit,
}: {
  phrases: Phrase[];
  onExit: () => void;
}) {
  const [index, setIndex] = useState(0);
  const [status, setStatus] = useState<Status>({ kind: "playing", slow: false });
  const recording = useRef<Recording | null>(null);
  const phrase = phrases[index];

  useEffect(() => {
    if (status.kind !== "playing") return;
    let current = true;
    void play(phrase.text, status.slow).then(() => {
      if (current) setStatus({ kind: "ready" });
    });
    return () => {
      current = false;
      hush();
    };
  }, [status, phrase]);

  const next = useCallback(() => {
    if (index + 1 < phrases.length) {
      setIndex(index + 1);
      setStatus({ kind: "playing", slow: false });
    } else {
      onExit();
    }
  }, [index, phrases.length, onExit]);

  useEffect(() => {
    if (status.kind !== "result") return;
    const again = status.outcome === "not_yet";
    const timer = window.setTimeout(() => {
      if (again) setStatus({ kind: "playing", slow: true });
      else next();
    }, pause);
    return () => window.clearTimeout(timer);
  }, [status, next]);

  async function pressDisc() {
    if (status.kind === "recording") {
      recording.current?.stop();
      return;
    }

    hush();
    try {
      const session = await record();
      recording.current = session;
      setStatus({ kind: "recording" });

      const audio = await session.done;
      recording.current = null;

      const outcome = await postAttempt(phrase.id, audio);
      if (outcome === "understood") chime();
      else softTone();
      setStatus({ kind: "result", outcome });
    } catch {
      recording.current = null;
      setStatus({ kind: "ready" });
    }
  }

  const speed = status.kind === "playing" ? (status.slow ? "slow" : "normal") : undefined;
  const outcome = status.kind === "result" ? status.outcome : undefined;

  return (
    <main
      className="practice"
      style={{ "--countdown": `${limit}ms` } as CSSProperties}
      data-status={status.kind}
      data-speed={speed}
      data-outcome={outcome}
    >
      <div className="dots">
        {phrases.map((item, position) => (
          <span key={item.id} className="dot" data-here={position === index || undefined} />
        ))}
      </div>

      <div className="card">
        <div className="picture">
          <img src={base + phrase.image_url} alt="" />
        </div>

        <div className="listen">
          <button
            className="round play"
            aria-label="Hear it"
            onClick={() => setStatus({ kind: "playing", slow: false })}
          >
            <Play />
          </button>
          <button
            className="round slow"
            aria-label="Hear it slowly"
            onClick={() => setStatus({ kind: "playing", slow: true })}
          >
            <Turtle />
          </button>
        </div>
      </div>

      <div className="disc-slot">
        <svg className="ring" viewBox="0 0 168 168" fill="none" aria-hidden focusable="false">
          <circle className="ring-track" cx="84" cy="84" r="78" strokeWidth={9} />
          <circle className="ring-fill" cx="84" cy="84" r="78" strokeWidth={9} strokeLinecap="round" />
        </svg>
        <button className="disc" aria-label="Say it" onClick={pressDisc}>
          <DiscFace status={status} />
        </button>
      </div>

      <div className="nav">
        <button className="round" aria-label="Back to categories" onClick={onExit}>
          <Grid />
        </button>
        <button className="round forward" aria-label="Next phrase" onClick={next}>
          <Arrow />
        </button>
      </div>
    </main>
  );
}

function DiscFace({ status }: { status: Status }) {
  if (status.kind === "recording") return <Bars />;
  if (status.kind !== "result") return <Mic />;
  return status.outcome === "understood" ? <Check /> : <Loop />;
}
