import { memo, useMemo, useState } from "react";
import { useFiltersStore } from "../../features/filters/filtersStore";
import { useSongs } from "../../features/songs/useSongs";
import SongDataPoint from "./SongDataPoint";
import { MOOD_OPTIONS } from "../../features/filters/moodOptions";
import { moodTextClass } from "../../features/graphs/moodTextColours";

const CONNECTION_ROWS_ALWAYS_VISIBLE = 5;

const MAX_POINTS_PER_ROW = 50;
const MIN_ROW_GAP = 14;

const BASE_NOTE_SIZE = 30;
const MAX_NOTE_SIZE = 52;
const NOTE_GROWTH_PER_POINT = 3;

function clampWeight(weight) {
  return Math.max(0, Math.min(10, Number(weight) || 0));
}

function distributeCountsEvenly(total, rows) {
  if (!rows || total <= 0) return [];

  const base = Math.floor(total / rows);
  const remainder = total % rows;

  return Array.from(
    { length: rows },
    (_, index) => base + (index < remainder ? 1 : 0),
  );
}

const MemoSongDataPoint = memo(SongDataPoint);

export default function ParallelCoordinatesPlot({
  width = 750,
  height = 350,
}) {
  const filters = useFiltersStore((state) => state.filters);
  const { data } = useSongs(filters);

  const songs = data ?? [];

  const [hoveredSongIndex, setHoveredSongIndex] = useState(null);
  const [clickedSongIndex, setClickedSongIndex] = useState(null);

  const activeSongIndex = hoveredSongIndex ?? clickedSongIndex;

  const layout = useMemo(() => {
    const safeWidth = Math.max(width, 320);
    const safeHeight = Math.max(height, 220);

    const labelX = safeWidth * 0.115;
    const lineStartX = safeWidth * 0.145;
    const lineEndX = safeWidth * 0.915;

    const topY = safeHeight * 0.2;
    const linesBlockHeight = safeHeight * 0.5;
    const lineGap =
      MOOD_OPTIONS.length > 1
        ? linesBlockHeight / (MOOD_OPTIONS.length - 1)
        : 0;

    const lineYByMood = Object.fromEntries(
      MOOD_OPTIONS.map((mood, index) => [mood, topY + index * lineGap]),
    );

    const getLineY = (emotion) => lineYByMood[emotion] ?? topY;

    const getNoteX = (weight) => {
      const normalized = clampWeight(weight) / 10;
      return lineStartX + normalized * (lineEndX - lineStartX);
    };

    const count = songs.length;

    if (!count) {
      return {
        safeWidth,
        safeHeight,
        contentHeight: safeHeight,
        labelX,
        lineStartX,
        lineEndX,
        getLineY,
        getNoteX,
        pointSize: 16,
        pointPositions: [],
        visibleSongCount: 0,
        noteItems: [],
        lineLabels: MOOD_OPTIONS.map((mood) => ({
          mood,
          y: getLineY(mood),
          className: moodTextClass[mood] ?? "text-white",
        })),
        pathItems: [],
      };
    }

    const rowCount = Math.ceil(count / MAX_POINTS_PER_ROW);
    const rowSongCounts = distributeCountsEvenly(count, rowCount);

    const firstPointRowY = safeHeight * 0.78;
    const bottomPadding = safeHeight * 0.08;
    const bundleOffset = Math.min(32, safeHeight * 0.11);

    const visibleRowCount = rowCount;
    const rowGap = visibleRowCount <= 1 ? 0 : MIN_ROW_GAP;

    const pointRowYs = Array.from(
      { length: visibleRowCount },
      (_, rowIndex) => firstPointRowY + rowIndex * rowGap,
    );

    const bundleYs = pointRowYs.map((pointRowY) => pointRowY - bundleOffset);

    const contentHeight =
      visibleRowCount <= 1
        ? safeHeight
        : Math.max(
            safeHeight,
            pointRowYs[pointRowYs.length - 1] + bottomPadding,
          );

    let globalPointSize = 16;
    const minPointSize = 4;
    const maxPointSize = 16;
    const usableWidth = lineEndX - lineStartX;

    for (let rowIndex = 0; rowIndex < rowCount; rowIndex += 1) {
      const rowCountValue = rowSongCounts[rowIndex];
      if (!rowCountValue) continue;

      const sizeForRow =
        rowCountValue === 1
          ? maxPointSize
          : Math.min(
              maxPointSize,
              Math.max(minPointSize, usableWidth / (rowCountValue + 1)),
            );

      globalPointSize = Math.min(globalPointSize, sizeForRow);
    }

    const pointPositions = new Array(count);
    let visibleSongCount = 0;
    let startIndex = 0;

    for (let rowIndex = 0; rowIndex < rowCount; rowIndex += 1) {
      const rowCountValue = rowSongCounts[rowIndex];
      const pointRowY = pointRowYs[rowIndex];

      if (rowCountValue === 1) {
        pointPositions[startIndex] = {
          x: (lineStartX + lineEndX) / 2,
          y: pointRowY,
          rowIndex,
        };
      } else {
        const step = usableWidth / (rowCountValue - 1);

        for (let i = 0; i < rowCountValue; i += 1) {
          pointPositions[startIndex + i] = {
            x: lineStartX + i * step,
            y: pointRowY,
            rowIndex,
          };
        }
      }

      visibleSongCount += rowCountValue;
      startIndex += rowCountValue;
    }

    const pathItems = [];
    const noteGroupsMap = new Map();

    for (let songIndex = 0; songIndex < count; songIndex += 1) {
      const song = songs[songIndex];
      const components = song.emotion_components ?? [];
      const pointPosition = pointPositions[songIndex];
      const isVisibleSong = Boolean(pointPosition);
      const isSongActive = activeSongIndex === songIndex;

      for (
        let componentIndex = 0;
        componentIndex < components.length;
        componentIndex += 1
      ) {
        const component = components[componentIndex];
        const clampedWeight = clampWeight(component.weight);
        const noteX = getNoteX(clampedWeight);
        const noteY = getLineY(component.emotion);
        const className = moodTextClass[component.emotion] ?? "text-white";

        const groupKey = `${component.emotion}-${clampedWeight.toFixed(3)}`;
        const existingGroup = noteGroupsMap.get(groupKey);

        if (existingGroup) {
          existingGroup.count += 1;
          existingGroup.isActive = existingGroup.isActive || isSongActive;
        } else {
          noteGroupsMap.set(groupKey, {
            key: `note-${groupKey}`,
            x: noteX,
            y: noteY,
            className,
            count: 1,
            isActive: isSongActive,
          });
        }

        if (!isVisibleSong) continue;

        const bundleY = bundleYs[pointPosition.rowIndex] ?? pointPosition.y - 24;
        const controlY1 = bundleY - safeHeight * 0.18;
        const controlY2 = noteY + safeHeight * 0.18;

        pathItems.push({
          key: `path-${songIndex}-${componentIndex}`,
          songIndex,
          className,
          isSongActive,
          isAlwaysVisibleRow:
            (pointPosition.rowIndex ?? 0) < CONNECTION_ROWS_ALWAYS_VISIBLE,
          d: `
            M ${pointPosition.x} ${pointPosition.y}
            L ${pointPosition.x} ${bundleY}
            C ${pointPosition.x} ${controlY1},
              ${noteX} ${controlY2},
              ${noteX} ${noteY}
          `,
        });
      }
    }

    const noteItems = Array.from(noteGroupsMap.values()).map((group) => ({
      ...group,
      fontSize: Math.min(
        MAX_NOTE_SIZE,
        BASE_NOTE_SIZE + (group.count - 1) * NOTE_GROWTH_PER_POINT,
      ),
    }));

    return {
      safeWidth,
      safeHeight,
      contentHeight,
      labelX,
      lineStartX,
      lineEndX,
      getLineY,
      pointSize: globalPointSize,
      pointPositions,
      visibleSongCount,
      noteItems,
      pathItems,
      lineLabels: MOOD_OPTIONS.map((mood) => ({
        mood,
        y: getLineY(mood),
        className: moodTextClass[mood] ?? "text-white",
      })),
    };
  }, [songs, width, height, activeSongIndex]);

  if (!songs.length) {
    return (
      <div className="flex h-full items-center justify-center text-white">
        <p className="font-madimi text-2xl">No songs found.</p>
      </div>
    );
  }

  const inactivePaths = layout.pathItems.filter(
  (path) => !path.isSongActive && path.isAlwaysVisibleRow,
);
  const activePaths = layout.pathItems.filter((path) => path.isSongActive);

  return (
    <div className="flex h-full w-full items-center justify-center text-white">
      <div
        data-graph-scroll-container="true"
        className="custom-scrollbar overflow-y-auto overflow-x-hidden"
        style={{ width: `${width}px`, height: `${height}px` }}
      >
        <div
          className="relative"
          style={{ width: `${width}px`, height: `${layout.contentHeight}px` }}
        >
          <svg
            width={width}
            height={layout.contentHeight}
            viewBox={`0 0 ${width} ${layout.contentHeight}`}
            className="absolute inset-0 z-0"
          >
            {layout.lineLabels.map(({ mood, y }) => (
              <line
                key={mood}
                x1={layout.lineStartX}
                y1={y}
                x2={layout.lineEndX}
                y2={y}
                stroke="white"
                strokeWidth="4"
                opacity="0.95"
                strokeLinecap="round"
              />
            ))}

            {inactivePaths.map((path) => (
              <path
                key={path.key}
                d={path.d}
                fill="none"
                stroke="white"
                strokeWidth="0.5"
                opacity="0.1"
                strokeLinecap="round"
              />
            ))}
          </svg>

          {layout.lineLabels.map(({ mood, y, className }) => (
            <div
              key={mood}
              className={`pointer-events-none absolute z-20 font-madimi text-[14px] leading-none ${className}`}
              style={{
                left: `${layout.labelX}px`,
                top: `${y}px`,
                transform: "translate(-100%, -52%)",
              }}
            >
              {mood}
            </div>
          ))}

          {layout.noteItems.map((note) => (
            <div
              key={note.key}
              className={`pointer-events-none absolute z-25 font-madimi leading-none ${note.className}`}
              style={{
                left: `${note.x}px`,
                top: `${note.y}px`,
                fontSize: `${note.fontSize}px`,
                transform: "translate(-50%, -62%)",
                filter: note.isActive ? "drop-shadow(0 0 6px white)" : "none",
              }}
            >
              ♪
            </div>
          ))}

          {songs.map((song, songIndex) => {
            const pointPosition = layout.pointPositions[songIndex];
            if (!pointPosition) return null;

            const isActive = activeSongIndex === songIndex;

            return (
              <div
                key={`point-${song.title}-${song.author}-${song.year}-${songIndex}`}
                className="absolute"
                style={{
                  left: `${pointPosition.x}px`,
                  top: `${pointPosition.y}px`,
                  transform: "translate(-50%, -50%)",
                  zIndex: isActive ? 999999 : songIndex,
                }}
              >
                <MemoSongDataPoint
                  song={song}
                  size={layout.pointSize}
                  isActive={isActive}
                  activeColor="#6874ff"
                  pointX={pointPosition.x}
                  pointY={pointPosition.y}
                  boxWidth={width}
                  boxHeight={height}
                  onMouseEnter={() => setHoveredSongIndex(songIndex)}
                  onMouseLeave={() =>
                    setHoveredSongIndex((current) =>
                      current === songIndex ? null : current,
                    )
                  }
                  onClick={() =>
                    setClickedSongIndex((current) =>
                      current === songIndex ? null : songIndex,
                    )
                  }
                />
              </div>
            );
          })}

          <svg
            width={width}
            height={layout.contentHeight}
            viewBox={`0 0 ${width} ${layout.contentHeight}`}
            className="pointer-events-none absolute inset-0 z-[15]"
          >
            <defs>
              <filter id="activeGlow" x="-50%" y="-50%" width="200%" height="200%">
                <feDropShadow
                  dx="0"
                  dy="0"
                  stdDeviation="3"
                  floodColor="white"
                  floodOpacity="0.9"
                />
              </filter>
            </defs>

            {activePaths.map((path) => (
              <g
                key={path.key}
                className={path.className}
                filter="url(#activeGlow)"
              >
                <path
                  d={path.d}
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                />
              </g>
            ))}
          </svg>
        </div>
      </div>
    </div>
  );
}