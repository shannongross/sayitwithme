export const limit = 8_000;

export type Recording = {
  stop: () => void;
  done: Promise<Blob>;
};

function audioType() {
  if (MediaRecorder.isTypeSupported("audio/webm;codecs=opus")) {
    return "audio/webm;codecs=opus";
  }
  return "audio/mp4";
}

export async function record(): Promise<Recording> {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const recorder = new MediaRecorder(stream, { mimeType: audioType() });
  const parts: BlobPart[] = [];
  let timer = 0;

  recorder.addEventListener("dataavailable", (event) => parts.push(event.data));

  const done = new Promise<Blob>((resolve) => {
    recorder.addEventListener("stop", () => {
      window.clearTimeout(timer);
      stream.getTracks().forEach((track) => track.stop());
      resolve(new Blob(parts, { type: recorder.mimeType }));
    });
  });

  recorder.start();
  timer = window.setTimeout(() => recorder.stop(), limit);

  return {
    stop: () => {
      if (recorder.state === "recording") recorder.stop();
    },
    done,
  };
}
