export default function SongPointPopup({ song }) {
  if (!song) return null;

  const lines = song.text
    ? song.text
        .split(/(?=[А-ЯA-Z])/)
        .map((line) => line.trim())
        .filter(Boolean)
    : [];

  return (
    <div
      className="
        custom-scrollbar
        w-40 max-h-25 overflow-y-auto rounded-lg border border-gray-200
        bg-white p-4 shadow-lg
      "
    >
      <div className="space-y-3 text-sm">
        <div>
          <p className="font-madimi text-blue-pastel">Title</p>
          <p className="font-afacad text-black break-words">{song.title}</p>
        </div>

        <div>
          <p className="font-madimi text-blue-pastel">Author</p>
          <p className="font-afacad text-black break-words">{song.author}</p>
        </div>

        <div>
          <p className="font-madimi text-blue-pastel">Genre</p>
          <p className="font-afacad text-black break-words">{song.genre}</p>
        </div>

        <div>
          <p className="font-madimi text-blue-pastel">Year</p>
          <p className="font-afacad text-black">{song.year}</p>
        </div>

        <div>
          <p className="font-madimi text-blue-pastel">Text</p>

          <div className="font-afacad text-black space-y-1 break-words">
            {lines.map((line, i) => (
              <p key={i}>{line}</p>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}