import { useMemo, useState } from "react";
import SongPointPopup from "../ui/SongPointPopup";
import { MOOD_OPTIONS } from "../../features/filters/moodOptions";

const MOOD_COLORS = {
  anger: "var(--color-red-pastel)",
  anticipation: "var(--color-orange-pastel)",
  happiness: "var(--color-yellow-pastel)",
  disgust: "var(--color-green-pastel)",
  sadness: "var(--color-blue-pastel)",
  fear: "var(--color-purple-pastel)",
};

const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

export default function ParallelCoordinatesChart({
  songs = [],
  width = 1100,
  height = 650,
}) {
  const [hoveredSongIndex, setHoveredSongIndex] = useState(null);
  const [clickedSongIndex, setClickedSongIndex] = useState(null);

  const activeSongIndex = hoveredSongIndex ?? clickedSongIndex;

  const layout = useMemo(() => {
    const leftLabelX = 140;
    const lineStartX = 230;
    const lineEndX = width - 70;
    const topY = 120;
    const lineGap = 72;
    const bottomY = height - 60;
    const stemTopY = height - 150;

    const moodY = Object.fromEntries(
      MOOD_OPTIONS.map((mood, index) => [mood, topY + index * lineGap]),
    );

    const n = songs.length;
    const pointXs =
      n <= 1
        ? [lineStartX]
        : songs.map(
            (_, index) =>
              lineStartX + (index * (lineEndX - lineStartX)) / (n - 1),
          );

    return {
      leftLabelX,
      lineStartX,
      lineEndX,
      topY,
      lineGap,
      bottomY,
      stemTopY,
      moodY,
      pointXs,
    };
  }, [songs, width, height]);

  if (!songs.length) {
    return (
      <div className="flex h-full items-center justify-center text-white">
        <p className="font-afacad text-xl">No songs found.</p>
      </div>
    );
  }

  const buildConnectionPath = (pointX, mood, weight) => {
    const targetY = layout.moodY[mood];
    const normalizedWeight = clamp(weight, 0, 10) / 10;
    const targetX =
      layout.lineStartX +
      normalizedWeight * (layout.lineEndX - layout.lineStartX);

    const stemY = layout.stemTopY;

    return `
      M ${pointX} ${layout.bottomY}
      L ${pointX} ${stemY}
      C ${pointX} ${stemY - 8},
        ${targetX} ${stemY - 8},
        ${targetX} ${targetY}
    `;
  };

  return (
    <div className="relative flex h-full w-full items-center justify-center overflow-visible">
      <div
        className="relative"
        style={{
          width: `${width}px`,
          height: `${height}px`,
        }}
      >
        <svg
          width={width}
          height={height}
          viewBox={`0 0 ${width} ${height}`}
          className="overflow-visible"
        >
          <defs>
            <filter id="activeWhiteGlow" x="-50%" y="-50%" width="200%" height="200%">
              <feDropShadow dx="0" dy="0" stdDeviation="4" floodColor="white" floodOpacity="0.9" />
            </filter>
          </defs>

          {/* 6 horizontal mood lines */}
          {MOOD_OPTIONS.map((mood) => (
            <g key={mood}>
              <text
                x={layout.leftLabelX}
                y={layout.moodY[mood]}
                textAnchor="end"
                dominantBaseline="middle"
                className="font-madimi text-[28px]"
                fill={MOOD_COLORS[mood]}
              >
                {mood}
              </text>

              <line
                x1={layout.lineStartX}
                y1={layout.moodY[mood]}
                x2={layout.lineEndX}
                y2={layout.moodY[mood]}
                stroke="white"
                strokeWidth="4"
                strokeLinecap="round"
              />
            </g>
          ))}

          {/* 0 and 1 markers */}
          <text
            x={layout.lineStartX}
            y={70}
            textAnchor="middle"
            className="font-madimi text-[28px]"
            fill="white"
          >
            0
          </text>

          <text
            x={layout.lineEndX}
            y={70}
            textAnchor="middle"
            className="font-madimi text-[28px]"
            fill="white"
          >
            1
          </text>

          {/* connection lines */}
          {songs.map((song, songIndex) => {
            const isActive = activeSongIndex === songIndex;
            const pointX = layout.pointXs[songIndex];
            const components = song.emotion_components ?? [];

            return (
              <g key={`connections-${songIndex}`}>
                {components.map((component, componentIndex) => {
                  const mood = component.emotion;
                  const color = MOOD_COLORS[mood] ?? "white";
                  const path = buildConnectionPath(
                    pointX,
                    mood,
                    component.weight ?? 0,
                  );

                  return (
                    <path
                      key={`${songIndex}-${componentIndex}-${mood}`}
                      d={path}
                      fill="none"
                      stroke={isActive ? color : "white"}
                      strokeWidth="1.5"
                      strokeOpacity={isActive ? 1 : 0.5}
                      filter={isActive ? "url(#activeWhiteGlow)" : undefined}
                      className="transition-all duration-200"
                    />
                  );
                })}
              </g>
            );
          })}

          {/* note symbols */}
          {songs.map((song, songIndex) => {
            const components = song.emotion_components ?? [];

            return components.map((component, componentIndex) => {
              const mood = component.emotion;
              const weight = clamp(component.weight ?? 0, 0, 10);
              const x =
                layout.lineStartX +
                (weight / 10) * (layout.lineEndX - layout.lineStartX);
              const y = layout.moodY[mood];
              const isActive = activeSongIndex === songIndex;

              return (
                <text
                  key={`note-${songIndex}-${componentIndex}-${mood}`}
                  x={x}
                  y={y}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fontSize={34}
                  fill={MOOD_COLORS[mood] ?? "white"}
                  filter={isActive ? "url(#activeWhiteGlow)" : undefined}
                  opacity={isActive ? 1 : 0.95}
                  className="select-none transition-all duration-200"
                >
                  ♪
                </text>
              );
            });
          })}

          {/* year labels - optional visual reference like in your mock */}
          <text
            x={layout.lineStartX - 10}
            y={height - 5}
            textAnchor="end"
            className="font-madimi text-[28px]"
            fill="white"
          >
            1969
          </text>

          <text
            x={layout.lineEndX + 30}
            y={height - 5}
            textAnchor="start"
            className="font-madimi text-[28px]"
            fill="white"
          >
            2004
          </text>
        </svg>

        {/* bottom data points */}
        {songs.map((song, songIndex) => {
          const pointX = layout.pointXs[songIndex];
          const isHovered = hoveredSongIndex === songIndex;
          const isClicked = clickedSongIndex === songIndex;
          const isActive = isHovered || isClicked;

          const size = isActive ? 28 : 24;

          return (
            <div
              key={`point-${songIndex}-${song.title}-${song.year}`}
              className="absolute -translate-x-1/2 -translate-y-1/2"
              style={{
                left: `${pointX}px`,
                top: `${layout.bottomY}px`,
                zIndex: isActive ? 30 : songIndex + 1,
              }}
              onMouseEnter={() => setHoveredSongIndex(songIndex)}
              onMouseLeave={() => setHoveredSongIndex(null)}
            >
              <button
                type="button"
                aria-label={`Open info for ${song.title}`}
                onClick={() =>
                  setClickedSongIndex((prev) =>
                    prev === songIndex ? null : songIndex,
                  )
                }
                className="cursor-pointer rounded-full transition-all duration-200 ease-out"
                style={{
                  width: `${size}px`,
                  height: `${size}px`,
                  backgroundColor: "white",
                  boxShadow: isActive
                    ? "0 0 12px rgba(255,255,255,0.95)"
                    : "0 0 8px rgba(255,255,255,0.65)",
                }}
              />

              {isActive && (
                <div className="absolute left-1/2 top-full z-50 mt-3 -translate-x-1/2">
                  <SongPointPopup song={song} />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}