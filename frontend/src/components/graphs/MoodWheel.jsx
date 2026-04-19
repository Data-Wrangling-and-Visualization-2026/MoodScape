import { useMemo, useRef, useState } from "react";
import { MOOD_OPTIONS } from "../../features/filters/moodOptions";
import { useFiltersStore } from "../../features/filters/filtersStore";
import { useSongs } from "../../features/songs/useSongs";
import SongDataPoint from "./SongDataPoint";

const moodFillClasses = {
  anger: {
    strong: "fill-[#FF7676]",
    default: "fill-red-pastel",
    mid: "fill-[#FF9797]",
    soft: "fill-[#FFBDBD]",
  },
  anticipation: {
    strong: "fill-[#FF9950]",
    default: "fill-orange-pastel",
    mid: "fill-[#FFBC8D]",
    soft: "fill-[#FFCFAD]",
  },
  happiness: {
    strong: "fill-[#FFF757]",
    default: "fill-yellow-pastel",
    mid: "fill-[#FFFA97]",
    soft: "fill-[#FFFCC2]",
  },
  disgust: {
    strong: "fill-[#65FF6B]",
    default: "fill-green-pastel",
    mid: "fill-[#AFFFB2]",
    soft: "fill-[#D1FFD2]",
  },
  sadness: {
    strong: "fill-[#5865FF]",
    default: "fill-blue-pastel",
    mid: "fill-[#8E97FF]",
    soft: "fill-[#B0B6FF]",
  },
  fear: {
    strong: "fill-[#B766FF]",
    default: "fill-purple-pastel",
    mid: "fill-[#D3A0FF]",
    soft: "fill-[#E7CCFF]",
  },
};

function polarToCartesian(cx, cy, radius, angleInDegrees) {
  const angleInRadians = ((angleInDegrees - 90) * Math.PI) / 180;

  return {
    x: cx + radius * Math.cos(angleInRadians),
    y: cy + radius * Math.sin(angleInRadians),
  };
}

function describeRingSegment(
  cx,
  cy,
  innerRadius,
  outerRadius,
  startAngle,
  endAngle,
) {
  const outerStart = polarToCartesian(cx, cy, outerRadius, startAngle);
  const outerEnd = polarToCartesian(cx, cy, outerRadius, endAngle);

  const innerEnd = polarToCartesian(cx, cy, innerRadius, endAngle);
  const innerStart = polarToCartesian(cx, cy, innerRadius, startAngle);

  const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";

  return [
    `M ${outerStart.x} ${outerStart.y}`,
    `A ${outerRadius} ${outerRadius} 0 ${largeArcFlag} 1 ${outerEnd.x} ${outerEnd.y}`,
    `L ${innerEnd.x} ${innerEnd.y}`,
    `A ${innerRadius} ${innerRadius} 0 ${largeArcFlag} 0 ${innerStart.x} ${innerStart.y}`,
    "Z",
  ].join(" ");
}

function getPointerAngle(clientX, clientY, element) {
  const rect = element.getBoundingClientRect();
  const cx = rect.left + rect.width / 2;
  const cy = rect.top + rect.height / 2;

  const dx = clientX - cx;
  const dy = clientY - cy;

  return (Math.atan2(dy, dx) * 180) / Math.PI;
}

function describeArc(cx, cy, radius, startAngle, endAngle) {
  const start = polarToCartesian(cx, cy, radius, startAngle);
  const end = polarToCartesian(cx, cy, radius, endAngle);

  const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";

  return [
    `M ${start.x} ${start.y}`,
    `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${end.x} ${end.y}`,
  ].join(" ");
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function seededUnitFromString(key) {
  let hash = 2166136261;

  for (let i = 0; i < key.length; i += 1) {
    hash ^= key.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }

  return ((hash >>> 0) % 1000000) / 1000000;
}

function getSongKey(song, index) {
  return [
    song?.id ?? "",
    song?.track_id ?? "",
    song?.title ?? "",
    song?.artist ?? "",
    song?.year ?? "",
    index,
  ].join("|");
}

function getDominantComponent(song) {
  const components = Array.isArray(song?.emotion_components)
    ? song.emotion_components
    : [];

  if (!components.length) return null;

  let best = null;

  for (const component of components) {
    if (
      !component ||
      typeof component.weight !== "number" ||
      !MOOD_OPTIONS.includes(component.emotion)
    ) {
      continue;
    }

    if (!best || component.weight > best.weight) {
      best = component;
    }
  }

  return best;
}

export default function MoodWheel({
  width = 750,
  height = 350,
}) {
  const filters = useFiltersStore((state) => state.filters);
  const { data } = useSongs(filters);
  const songs = Array.isArray(data) ? data : [];

  const [rotation, setRotation] = useState(0);
  const [activePointKey, setActivePointKey] = useState(null);

  const dragStateRef = useRef({
    isDragging: false,
    lastPointerAngle: 0,
  });

  const wheelRef = useRef(null);

  const size = height;
  const center = size / 2;
  const outerRadius = size * 0.36;
  const innerRadius = size * 0.06;
  const bandWidth = (outerRadius - innerRadius) / 4;

  const sectors = useMemo(() => {
    return MOOD_OPTIONS.map((mood, index) => {
      const sectorStart = -30 + index * 60;
      const sectorEnd = sectorStart + 60;

      return {
        mood,
        startAngle: sectorStart,
        endAngle: sectorEnd,
        fills: moodFillClasses[mood],
      };
    });
  }, []);

  const sectorByMood = useMemo(() => {
    return Object.fromEntries(sectors.map((sector) => [sector.mood, sector]));
  }, [sectors]);

  const plottedPoints = useMemo(() => {
    const pointSize = clamp(size * 0.02, 8, 16);
    const pointPadding = pointSize * 0.9;
    const angularPadding = 6;

    return songs
      .map((song, index) => {
        const dominant = getDominantComponent(song);
        if (!dominant) return null;

        const sector = sectorByMood[dominant.emotion];
        if (!sector) return null;

        const key = getSongKey(song, index);

        const angleSeed = seededUnitFromString(`${key}-angle`);
        const jitterSeed = seededUnitFromString(`${key}-radius-jitter`);

        const clampedWeight = clamp(dominant.weight, 0, 10);

        const usableInnerRadius = innerRadius + pointPadding;
        const usableOuterRadius = outerRadius - pointPadding;

        const baseRadius =
          usableInnerRadius +
          (clampedWeight / 10) * (usableOuterRadius - usableInnerRadius);

        const maxRadiusJitter = Math.min(bandWidth * 0.2, pointSize * 0.9);
        const radius = baseRadius + (jitterSeed * 2 - 1) * maxRadiusJitter;

        const angle =
          sector.startAngle +
          angularPadding +
          angleSeed *
            Math.max(1, sector.endAngle - sector.startAngle - angularPadding * 2);

        const { x, y } = polarToCartesian(center, center, radius, angle);

        return {
          key,
          song,
          mood: dominant.emotion,
          weight: dominant.weight,
          x,
          y,
          size: pointSize,
        };
      })
      .filter(Boolean);
  }, [
    songs,
    sectorByMood,
    size,
    innerRadius,
    outerRadius,
    bandWidth,
    center,
  ]);

  const handlePointerDown = (event) => {
    if (!wheelRef.current) return;

    event.currentTarget.setPointerCapture(event.pointerId);

    dragStateRef.current.isDragging = true;
    dragStateRef.current.lastPointerAngle = getPointerAngle(
      event.clientX,
      event.clientY,
      wheelRef.current,
    );
  };

  const handlePointerMove = (event) => {
    if (!dragStateRef.current.isDragging || !wheelRef.current) return;

    const nextPointerAngle = getPointerAngle(
      event.clientX,
      event.clientY,
      wheelRef.current,
    );

    const delta = nextPointerAngle - dragStateRef.current.lastPointerAngle;

    setRotation((prev) => prev + delta);
    dragStateRef.current.lastPointerAngle = nextPointerAngle;
  };

  const stopDragging = () => {
    dragStateRef.current.isDragging = false;
  };

  return (
    <div
      style={{
        "--box-width": `${width}px`,
        "--box-height": `${height}px`,
      }}
      className="relative h-[var(--box-height)] w-[var(--box-width)]"
    >
      <div
        ref={wheelRef}
        className="absolute left-0 top-0 flex h-[var(--box-height)] w-[var(--box-width)] touch-none items-center justify-center select-none"
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={stopDragging}
        onPointerCancel={stopDragging}
        onPointerLeave={stopDragging}
        style={{
          cursor: dragStateRef.current.isDragging ? "grabbing" : "grab",
        }}
      >
        <svg
          viewBox={`0 0 ${size} ${size}`}
          className="h-full w-full"
          style={{
            transform: `rotate(${rotation}deg)`,
            transformOrigin: "50% 50%",
          }}
        >
          {sectors.map((sector) => {
            const r1 = innerRadius;
            const r2 = innerRadius + bandWidth;
            const r3 = innerRadius + bandWidth * 2;
            const r4 = innerRadius + bandWidth * 3;
            const r5 = outerRadius;

            return (
              <g key={sector.mood}>
                <path
                  d={describeRingSegment(
                    center,
                    center,
                    r1,
                    r2,
                    sector.startAngle,
                    sector.endAngle,
                  )}
                  className={sector.fills.soft}
                />

                <path
                  d={describeRingSegment(
                    center,
                    center,
                    r2,
                    r3,
                    sector.startAngle,
                    sector.endAngle,
                  )}
                  className={sector.fills.mid}
                />

                <path
                  d={describeRingSegment(
                    center,
                    center,
                    r3,
                    r4,
                    sector.startAngle,
                    sector.endAngle,
                  )}
                  className={sector.fills.default}
                />

                <path
                  d={describeRingSegment(
                    center,
                    center,
                    r4,
                    r5,
                    sector.startAngle,
                    sector.endAngle,
                  )}
                  className={sector.fills.strong}
                />
              </g>
            );
          })}

          <circle cx={center} cy={center} r={innerRadius} fill="white" />

          <circle
            cx={center}
            cy={center}
            r={outerRadius}
            fill="none"
            stroke="white"
            strokeWidth="8"
          />

          <defs>
            {sectors.map((sector) => {
              const labelRadius = outerRadius + 10;
              const arcStart = sector.startAngle;
              const arcEnd = sector.endAngle;

              return (
                <path
                  key={`${sector.mood}-label-path`}
                  id={`mood-label-path-${sector.mood}`}
                  d={describeArc(center, center, labelRadius, arcStart, arcEnd)}
                  fill="none"
                />
              );
            })}
          </defs>

          {sectors.map((sector) => (
            <text
              key={`${sector.mood}-label`}
              className="fill-white font-madimi text-[18px]"
              style={{
                letterSpacing: "1.5px",
                textTransform: "uppercase",
              }}
            >
              <textPath
                href={`#mood-label-path-${sector.mood}`}
                startOffset="50%"
                textAnchor="middle"
              >
                {sector.mood.toUpperCase()}
              </textPath>
            </text>
          ))}
        </svg>

        <div
          className="pointer-events-none absolute left-1/2 top-1/2"
          style={{
            width: `${size}px`,
            height: `${size}px`,
            transform: `translate(-50%, -50%) rotate(${rotation}deg)`,
            transformOrigin: "50% 50%",
          }}
        >
          {plottedPoints.map((point) => (
            <div
              key={point.key}
              className="pointer-events-auto absolute"
              style={{
                left: `${point.x}px`,
                top: `${point.y}px`,
                transform: "translate(-50%, -50%)",
                zIndex: activePointKey === point.key ? 50 : 10,
              }}
            >
              <SongDataPoint
                song={point.song}
                size={point.size}
                isActive={activePointKey === point.key}
                activeColor="#131d3c"
                onMouseEnter={() => setActivePointKey(point.key)}
                onMouseLeave={() => setActivePointKey((current) => (
                  current === point.key ? null : current
                ))}
                onClick={() =>
                  setActivePointKey((current) =>
                    current === point.key ? null : point.key
                  )
                }
                pointX={point.x}
                pointY={point.y}
                boxWidth={width}
                boxHeight={height}
              />
            </div>
          ))}
        </div>
      </div>

      <div className="pointer-events-none absolute bottom-20 right-20 z-[60] flex flex-col items-end">
        <svg
          width="120"
          height="70"
          viewBox="0 0 120 70"
          className="overflow-visible"
        >
          <path
            d="M 108 58 C 95 20, 60 10, 38 10"
            fill="none"
            stroke="white"
            strokeWidth="3"
            strokeLinecap="round"
          />
          <path
            d="M 43 4 L 38 10 L 44 17"
            fill="none"
            stroke="white"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>

        <span className="mt-[-4px] font-madimi text-xl text-white">
          spin it!
        </span>
      </div>
    </div>
  );
}