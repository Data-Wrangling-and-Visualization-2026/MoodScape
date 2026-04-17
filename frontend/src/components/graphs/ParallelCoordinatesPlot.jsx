import { useMemo, useState } from "react";
import { useFiltersStore } from "../../features/filters/filtersStore";
import { useSongs } from "../../features/songs/useSongs";
import SongDataPoint from "./SongDataPoint";
import { MOOD_OPTIONS } from "../../features/filters/moodOptions";

const PLOT_WIDTH = 600;
const PLOT_HEIGHT = 270;

const LABEL_X = 50;
const LINE_START_X = 70;
const LINE_END_X = 600;

const TOP_Y = 20;
const LINE_GAP = 38;

const POINT_ROW_Y = 280;
const BUNDLE_Y = 248;

const moodTextClass = {
  anger: "text-red-pastel",
  anticipation: "text-orange-pastel",
  happiness: "text-yellow-pastel",
  disgust: "text-green-pastel",
  sadness: "text-blue-pastel",
  fear: "text-purple-pastel",
};

function clampWeight(weight) {
  return Math.max(0, Math.min(10, Number(weight) || 0));
}

function getLineY(emotion) {
  const index = MOOD_OPTIONS.indexOf(emotion);
  return TOP_Y + index * LINE_GAP;
}

function getNoteX(weight) {
  const normalized = clampWeight(weight) / 10;
  return LINE_START_X + normalized * (LINE_END_X - LINE_START_X);
}

export default function ParallelCoordinatesPlot() {
  const filters = useFiltersStore((state) => state.filters);
  const { data } = useSongs(filters);

  const songs = data ?? [];

  const [hoveredSongIndex, setHoveredSongIndex] = useState(null);
  const [clickedSongIndex, setClickedSongIndex] = useState(null);

  const activeSongIndex = hoveredSongIndex ?? clickedSongIndex;

  const { pointSize, pointXs } = useMemo(() => {
    const count = songs.length;

    if (!count) {
      return { pointSize: 16, pointXs: [] };
    }

    // ✅ Use EXACT same width as graph lines
    const usableWidth = LINE_END_X - LINE_START_X;

    const minPointSize = 8;
    const maxPointSize = 22;

    const totalGapWidth = 8 * Math.max(count - 1, 0);
    const availableWidth = usableWidth - totalGapWidth;

    let size = availableWidth / count;
    size = Math.max(minPointSize, Math.min(maxPointSize, size));

    const spacing = count > 1 ? (usableWidth - size) / (count - 1) : 0;

    const xs = songs.map((_, index) =>
      count === 1
        ? LINE_START_X + usableWidth / 2
        : LINE_START_X + size / 2 + index * spacing,
    );

    return { pointSize: size, pointXs: xs };
  }, [songs]);

  if (!songs.length) {
    return (
      <div className="flex h-full items-center justify-center text-white">
        <p className="font-madimi text-2xl">No songs found.</p>
      </div>
    );
  }

  return (
    <div className="flex h-full w-full items-center justify-center text-white">
      <div
        className="relative"
        style={{ width: `${PLOT_WIDTH}px`, height: `${PLOT_HEIGHT}px` }}
      >
        <svg
          width={PLOT_WIDTH}
          height={PLOT_HEIGHT}
          viewBox={`0 0 ${PLOT_WIDTH} ${PLOT_HEIGHT}`}
          className="absolute inset-0 overflow-visible"
        >
          <defs>
            <filter id="activeGlow" x="-50%" y="-50%" width="200%" height="200%">
              <feDropShadow dx="0" dy="0" stdDeviation="3" floodColor="white" floodOpacity="0.9" />
            </filter>
          </defs>

          {MOOD_OPTIONS.map((mood) => {
            const y = getLineY(mood);

            return (
              <line
                key={mood}
                x1={LINE_START_X}
                y1={y}
                x2={LINE_END_X}
                y2={y}
                stroke="white"
                strokeWidth="4"
                opacity="0.95"
                strokeLinecap="round"
              />
            );
          })}

          {songs.map((song, songIndex) => {
            const pointX = pointXs[songIndex];
            const isSongActive = activeSongIndex === songIndex;

            return (
              <g key={`${song.title}-${song.author}-${song.year}-${songIndex}`}>
                {(song.emotion_components ?? []).map((component, componentIndex) => {
                  const noteX = getNoteX(component.weight);
                  const noteY = getLineY(component.emotion);
                  const moodClass = moodTextClass[component.emotion] ?? "text-white";

                  const pathD = `
                    M ${pointX} ${POINT_ROW_Y}
                    L ${pointX} ${BUNDLE_Y}
                    C ${pointX} ${BUNDLE_Y - 65},
                      ${noteX} ${noteY + 55},
                      ${noteX} ${noteY}
                  `;

                  if (!isSongActive) {
                    return (
                      <path
                        key={componentIndex}
                        d={pathD}
                        fill="none"
                        stroke="white"
                        strokeWidth="0.5"
                        opacity="0.2"
                        strokeLinecap="round"
                      />
                    );
                  }

                  return (
                    <g key={componentIndex} className={moodClass} filter="url(#activeGlow)">
                      <path
                        d={pathD}
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                      />
                    </g>
                  );
                })}
              </g>
            );
          })}
        </svg>

        {MOOD_OPTIONS.map((mood) => {
          const y = getLineY(mood);

          return (
            <div
              key={mood}
              className={`pointer-events-none absolute font-madimi text-[14px] leading-none ${moodTextClass[mood]}`}
              style={{
                left: `${LABEL_X}px`,
                top: `${y}px`,
                transform: "translate(-100%, -52%)",
              }}
            >
              {mood}
            </div>
          );
        })}

        {songs.map((song, songIndex) =>
          (song.emotion_components ?? []).map((component, componentIndex) => {
            const noteX = getNoteX(component.weight);
            const noteY = getLineY(component.emotion);
            const isSongActive = activeSongIndex === songIndex;

            return (
              <div
                key={`note-${songIndex}-${componentIndex}`}
                className={`pointer-events-none absolute font-madimi text-[30px] leading-none ${
                  moodTextClass[component.emotion] ?? "text-white"
                }`}
                style={{
                  left: `${noteX}px`,
                  top: `${noteY}px`,
                  transform: "translate(-50%, -62%)",
                  filter: isSongActive ? "drop-shadow(0 0 6px white)" : "none",
                }}
              >
                ♪
              </div>
            );
          }),
        )}

        {songs.map((song, songIndex) => (
          <div
            key={`point-${song.title}-${song.author}-${song.year}-${songIndex}`}
            className="absolute"
            style={{
              left: `${pointXs[songIndex]}px`,
              top: `${POINT_ROW_Y}px`,
              transform: "translate(-50%, -50%)",
              zIndex: songIndex + 20,
            }}
          >
            <SongDataPoint
              song={song}
              size={pointSize}
              isActive={activeSongIndex === songIndex}
              onMouseEnter={() => setHoveredSongIndex(songIndex)}
              onMouseLeave={() => setHoveredSongIndex((current) => (current === songIndex ? null : current))}
              onClick={() =>
                setClickedSongIndex((current) => (current === songIndex ? null : songIndex))
              }
            />
          </div>
        ))}
      </div>
    </div>
  );
}