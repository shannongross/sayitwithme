export type Category = {
  id: string;
  image_url: string;
};

export type Phrase = {
  id: string;
  text: string;
  image_url: string;
};

export type Outcome = "understood" | "not_yet";

// Nothing on screen can say "the network is down", so a read waits and asks again.
async function read<T>(path: string): Promise<T[]> {
  for (;;) {
    try {
      const response = await fetch(path);
      if (response.ok) return await response.json();
    } catch {
      // A dropped connection and a refused request get the same treatment.
    }
    await new Promise((resume) => window.setTimeout(resume, 3_000));
  }
}

export function getCategories(): Promise<Category[]> {
  return read("/api/categories");
}

export function getPhrases(category: string): Promise<Phrase[]> {
  return read(`/api/categories/${category}`);
}

// A failed attempt reads as not-yet, because pressing the disc again is the move either way.
export async function postAttempt(phraseId: string, audio: Blob): Promise<Outcome> {
  const form = new FormData();
  form.append("phrase_id", phraseId);
  form.append("audio", audio, "attempt");

  const response = await fetch("/api/attempts", { method: "POST", body: form });
  if (!response.ok) return "not_yet";
  return (await response.json()).result;
}
