import SongPointPopup from "../ui/SongPointPopup";

export default function SongDataPoint({
  song,
  size = 16,
  isActive = false,
  onMouseEnter,
  onMouseLeave,
  onClick,
}) {
  const currentSize = isActive ? size * 1.25 : size;

  return (
    <div
      className="relative inline-flex items-center justify-center"
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      <button
        type="button"
        aria-label={`Open info for ${song.title}`}
        onClick={onClick}
        className="cursor-pointer rounded-full transition-all duration-200 ease-out"
        style={{
          width: `${currentSize}px`,
          height: `${currentSize}px`,
          backgroundColor: "white",
          boxShadow: isActive ? "0 0 10px rgba(255,255,255,0.95)" : "0 0 6px rgba(0,0,0,0.7)",
        }}
      />

      {isActive && (
        <div className="absolute left top-full z-50 mt-3">
          <SongPointPopup song={song} />
        </div>
      )}
    </div>
  );
}