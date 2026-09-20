import type { Category } from "./api";

export default function Categories({
  categories,
  onPick,
}: {
  categories: Category[];
  onPick: (id: string) => void;
}) {
  return (
    <main className="categories">
      {categories.map((category) => (
        <button
          key={category.id}
          className="tile"
          aria-label={category.id}
          onClick={() => onPick(category.id)}
        >
          <img src={category.image_url} alt="" />
        </button>
      ))}
    </main>
  );
}
