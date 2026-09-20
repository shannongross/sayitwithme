import { useCallback, useEffect, useState } from "react";

import { getCategories, getPhrases, type Category, type Phrase } from "./api";
import { prime } from "./audio";
import Categories from "./Categories";
import Practice from "./Practice";

export default function App() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [phrases, setPhrases] = useState<Phrase[] | null>(null);

  useEffect(() => {
    void getCategories().then(setCategories);
  }, []);

  // prime() runs before the await so it stays inside the tap that triggered it.
  async function openCategory(id: string) {
    prime();
    const found = await getPhrases(id);
    if (found.length > 0) setPhrases(found);
  }

  const exit = useCallback(() => setPhrases(null), []);

  if (phrases === null) {
    return <Categories categories={categories} onPick={openCategory} />;
  }
  return <Practice phrases={phrases} onExit={exit} />;
}
