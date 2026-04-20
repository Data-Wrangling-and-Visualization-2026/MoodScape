import { useMemo, useState } from "react";
import { Check } from "lucide-react";
import { useFiltersStore } from "../../features/filters/filtersStore";
import { useSongs } from "../../features/songs/useSongs";
import { moodTextClass } from "../../features/graphs/moodTextColours";
import { MOOD_OPTIONS } from "../../features/filters/moodOptions";

/* -------------------------------------------------------------------------- */
/*                                Color helpers                               */
/* -------------------------------------------------------------------------- */

const moodStrokeClass = {
  anger: "stroke-red-pastel",
  anticipation: "stroke-orange-pastel",
  happiness: "stroke-yellow-pastel",
  disgust: "stroke-green-pastel",
  sadness: "stroke-blue-pastel",
  fear: "stroke-purple-pastel",
};

const moodBgClass = {
  anger: "bg-red-pastel",
  anticipation: "bg-orange-pastel",
  happiness: "bg-yellow-pastel",
  disgust: "bg-green-pastel",
  sadness: "bg-blue-pastel",
  fear: "bg-purple-pastel",
};

const moodBorderClass = {
  anger: "border-red-pastel",
  anticipation: "border-orange-pastel",
  happiness: "border-yellow-pastel",
  disgust: "border-green-pastel",
  sadness: "border-blue-pastel",
  fear: "border-purple-pastel",
};

const moodHex = {
  anger: "#FF8E8E",
  anticipation: "#ffad73",
  happiness: "#fcf67a",
  disgust: "#90ff94",
  sadness: "#6874ff",
  fear: "#c588fb",
};

/* -------------------------------------------------------------------------- */
/*                             Geometry helper funcs                          */
/* -------------------------------------------------------------------------- */

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function buildSmoothLinePath(points, chartTop, chartBottom) {
  if (!points.length) return "";
  if (points.length === 1) {
    const p = points[0];
    return `M ${p.x} ${p.y}`;
  }

  let d = `M ${points[0].x} ${points[0].y}`;

  for (let i = 0; i < points.length - 1; i += 1) {
    const p0 = points[i - 1] ?? points[i];
    const p1 = points[i];
    const p2 = points[i + 1];
    const p3 = points[i + 2] ?? p2;

    const cp1x = p1.x + (p2.x - p0.x) / 6;
    const cp2x = p2.x - (p3.x - p1.x) / 6;

    let cp1y = p1.y + (p2.y - p0.y) / 6;
    let cp2y = p2.y - (p3.y - p1.y) / 6;

    cp1y = clamp(cp1y, chartTop, chartBottom);
    cp2y = clamp(cp2y, chartTop, chartBottom);

    const segMinY = Math.min(p1.y, p2.y);
    const segMaxY = Math.max(p1.y, p2.y);

    cp1y = clamp(cp1y, segMinY, segMaxY);
    cp2y = clamp(cp2y, segMinY, segMaxY);

    d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`;
  }

  return d;
}

function buildAreaPath(points, chartTop, chartBottomY) {
  if (!points.length) return "";

  const linePath = buildSmoothLinePath(points, chartTop, chartBottomY);
  const last = points[points.length - 1];
  const first = points[0];

  return `${linePath} L ${last.x} ${chartBottomY} L ${first.x} ${chartBottomY} Z`;
}

function getRoundYearTicks(minYear, maxYear) {
  if (!Number.isFinite(minYear) || !Number.isFinite(maxYear)) return [];

  const span = Math.max(0, maxYear - minYear);

  let step = 5;
  if (span > 80) step = 20;
  else if (span > 40) step = 10;

  const start = Math.ceil(minYear / step) * step;
  const ticks = [];

  for (let year = start; year <= maxYear; year += step) {
    if (year !== minYear && year !== maxYear) {
      ticks.push(year);
    }
  }

  return ticks;
}

/* -------------------------------------------------------------------------- */
/*                                Main component                              */
/* -------------------------------------------------------------------------- */

export default function LineGraph({ width = 750, height = 350 }) {
  const filters = useFiltersStore((state) => state.filters);
  const { data: songs = [] } = useSongs(filters);

  const [enabledMoods, setEnabledMoods] = useState(() =>
    MOOD_OPTIONS.reduce((acc, mood) => {
      acc[mood] = true;
      return acc;
    }, {}),
  );

  /* ------------------------------------------------------------------------ */
  /*                            Size-driven layout                            */
  /* ------------------------------------------------------------------------ */

  const layout = useMemo(() => {
    const safeWidth = Math.max(width, 320);
    const safeHeight = Math.max(height, 220);

    const rightLegendWidth = safeWidth * 0.2;
    const topPadding = safeHeight * 0.15;
    const leftPadding = safeWidth * 0.09;
    const rightPadding = safeWidth * 0.025;
    const bottomPadding = safeHeight * 0.14;

    const chartLeft = leftPadding;
    const chartRight = safeWidth - rightLegendWidth - rightPadding;
    const chartTop = topPadding;
    const chartBottom = safeHeight - bottomPadding;

    const chartWidth = Math.max(60, chartRight - chartLeft);
    const chartHeight = Math.max(60, chartBottom - chartTop);

    return {
      safeWidth,
      safeHeight,
      rightLegendWidth,
      topPadding,
      leftPadding,
      rightPadding,
      bottomPadding,
      chartLeft,
      chartRight,
      chartTop,
      chartBottom,
      chartWidth,
      chartHeight,

      axisStrokeWidth: clamp(Math.min(safeWidth, safeHeight) * 0.004, 1.25, 3),
      lineStrokeWidth: 1,
      gridStrokeWidth: clamp(
        Math.min(safeWidth, safeHeight) * 0.0025,
        0.7,
        1.5,
      ),
      legendFontSize: clamp(Math.min(safeWidth, safeHeight) * 0.039, 10, 15),
      axisFontSize: clamp(Math.min(safeWidth, safeHeight) * 0.042, 11, 16),
      roundYearFontSize: clamp(Math.min(safeWidth, safeHeight) * 0.032, 9, 12),
      yTickFontSize: clamp(Math.min(safeWidth, safeHeight) * 0.03, 8, 12),
      checkboxSize: clamp(Math.min(safeWidth, safeHeight) * 0.07, 15, 24),
      checkIconSize: clamp(Math.min(safeWidth, safeHeight) * 0.04, 9, 16),
      legendRowGap: clamp(safeHeight * 0.028, 7, 14),
      roundYearTickHeight: clamp(safeHeight * 0.028, 6, 11),
      titleFontSize: clamp(Math.min(safeWidth, safeHeight) * 0.05, 14, 22),
    };
  }, [width, height]);

  /* ------------------------------------------------------------------------ */
  /*                          Aggregate data by year                          */
  /* ------------------------------------------------------------------------ */

  const yearlyMoodAverages = useMemo(() => {
    if (!songs.length) return [];

    const yearMap = new Map();

    for (const song of songs) {
      const year = Number(song.year);
      if (!Number.isFinite(year)) continue;

      if (!yearMap.has(year)) {
        const initialMoodStats = {};
        for (const mood of MOOD_OPTIONS) {
          initialMoodStats[mood] = { sum: 0, count: 0 };
        }
        yearMap.set(year, initialMoodStats);
      }

      const yearStats = yearMap.get(year);
      const components = Array.isArray(song.emotion_components)
        ? song.emotion_components
        : [];

      for (const component of components) {
        const mood = component?.emotion;
        const weight = Number(component?.weight);

        if (!MOOD_OPTIONS.includes(mood)) continue;
        if (!Number.isFinite(weight)) continue;

        yearStats[mood].sum += weight;
        yearStats[mood].count += 1;
      }
    }

    return Array.from(yearMap.entries())
      .sort((a, b) => a[0] - b[0])
      .map(([year, stats]) => {
        const entry = { year };

        for (const mood of MOOD_OPTIONS) {
          const { sum, count } = stats[mood];
          entry[mood] = count > 0 ? sum / count : 0;
        }

        return entry;
      });
  }, [songs]);

  const minYear = yearlyMoodAverages[0]?.year ?? 0;
  const maxYear = yearlyMoodAverages[yearlyMoodAverages.length - 1]?.year ?? 0;

  /* ------------------------------------------------------------------------ */
  /*                         Convert values to SVG points                     */
  /* ------------------------------------------------------------------------ */

  const moodPaths = useMemo(() => {
    if (!yearlyMoodAverages.length) return {};

    const yearSpan = Math.max(1, maxYear - minYear);

    const valueToY = (value) => {
      const normalized = clamp(value / 10, 0, 1);
      return layout.chartBottom - normalized * layout.chartHeight;
    };

    const yearToX = (year) => {
      const normalized = (year - minYear) / yearSpan;
      return layout.chartLeft + normalized * layout.chartWidth;
    };

    const result = {};

    for (const mood of MOOD_OPTIONS) {
      const points = yearlyMoodAverages.map((entry) => ({
        x: yearToX(entry.year),
        y: valueToY(entry[mood]),
      }));

      result[mood] = {
        points,
        linePath: buildSmoothLinePath(
          points,
          layout.chartTop,
          layout.chartBottom,
        ),
        areaPath: buildAreaPath(points, layout.chartTop, layout.chartBottom),
      };
    }

    return result;
  }, [yearlyMoodAverages, minYear, maxYear, layout]);

  const roundYearTicks = useMemo(
    () => getRoundYearTicks(minYear, maxYear),
    [minYear, maxYear],
  );

  /* ------------------------------------------------------------------------ */
  /*                              Event handlers                              */
  /* ------------------------------------------------------------------------ */

  const toggleMood = (mood) => {
    setEnabledMoods((prev) => ({
      ...prev,
      [mood]: !prev[mood],
    }));
  };

  const yTicks = Array.from({ length: 11 }, (_, i) => i);
  const yearSpan = Math.max(1, maxYear - minYear);
  const yearToX = (year) => {
    const normalized = (year - minYear) / yearSpan;
    return layout.chartLeft + normalized * layout.chartWidth;
  };

  return (
    <div
      className="relative h-full w-full overflow-hidden rounded-lg bg-dark-blue"
      style={{ width, height }}
    >
      <svg
        width={width}
        height={height}
        viewBox={`0 0 ${width} ${height}`}
        className="block h-full w-full"
      >
        <defs>
          {MOOD_OPTIONS.map((mood) => (
            <linearGradient
              key={`gradient-${mood}`}
              id={`line-graph-gradient-${mood}`}
              x1="0"
              y1={layout.chartTop}
              x2="0"
              y2={layout.chartBottom}
              gradientUnits="userSpaceOnUse"
            >
              <stop offset="0%" stopColor={moodHex[mood]} stopOpacity="0.5" />
              <stop offset="100%" stopColor={moodHex[mood]} stopOpacity="0" />
            </linearGradient>
          ))}
        </defs>

        <text
          x={(layout.chartLeft + layout.chartRight) / 2}
          y={layout.chartTop * 0.6}
          fill="white"
          fontSize={layout.titleFontSize}
          fontFamily="Madimi One, sans-serif"
          textAnchor="middle"
          dominantBaseline="middle"
        >
          Average mood trend by year
        </text>

        {yTicks.map((tick) => {
          const y = layout.chartBottom - (tick / 10) * layout.chartHeight;

          return (
            <g key={`y-tick-${tick}`}>
              <line
                x1={layout.chartLeft}
                y1={y}
                x2={layout.chartRight}
                y2={y}
                stroke="white"
                strokeOpacity="0.08"
                strokeWidth={layout.gridStrokeWidth}
              />

              <text
                x={layout.chartLeft - width * 0.018}
                y={y}
                fill="white"
                fillOpacity="0.45"
                fontSize={layout.yTickFontSize}
                fontFamily="Madimi One, sans-serif"
                textAnchor="end"
                dominantBaseline="middle"
              >
                {tick}
              </text>
            </g>
          );
        })}

        {roundYearTicks.map((year) => {
          const x = yearToX(year);

          return (
            <g key={`round-year-${year}`}>
              <line
                x1={x}
                y1={layout.chartBottom}
                x2={x}
                y2={layout.chartBottom + layout.roundYearTickHeight}
                stroke="white"
                strokeOpacity="0.2"
                strokeWidth={layout.gridStrokeWidth}
              />

              <text
                x={x}
                y={
                  layout.chartBottom +
                  layout.roundYearTickHeight +
                  height * 0.018
                }
                fill="white"
                fillOpacity="0.35"
                fontSize={layout.roundYearFontSize}
                fontFamily="Madimi One, sans-serif"
                textAnchor="middle"
                dominantBaseline="hanging"
              >
                {year}
              </text>
            </g>
          );
        })}

        <line
          x1={layout.chartLeft}
          y1={layout.chartTop}
          x2={layout.chartLeft}
          y2={layout.chartBottom}
          stroke="white"
          strokeWidth={layout.axisStrokeWidth}
        />

        <line
          x1={layout.chartLeft}
          y1={layout.chartBottom}
          x2={layout.chartRight}
          y2={layout.chartBottom}
          stroke="white"
          strokeWidth={layout.axisStrokeWidth}
        />

        <line
          x1={layout.chartLeft}
          y1={layout.chartTop}
          x2={layout.chartLeft - width * 0.008}
          y2={layout.chartTop + height * 0.015}
          stroke="white"
          strokeWidth={layout.axisStrokeWidth}
        />
        <line
          x1={layout.chartLeft}
          y1={layout.chartTop}
          x2={layout.chartLeft + width * 0.008}
          y2={layout.chartTop + height * 0.015}
          stroke="white"
          strokeWidth={layout.axisStrokeWidth}
        />
        <line
          x1={layout.chartRight}
          y1={layout.chartBottom}
          x2={layout.chartRight - width * 0.01}
          y2={layout.chartBottom - height * 0.015}
          stroke="white"
          strokeWidth={layout.axisStrokeWidth}
        />
        <line
          x1={layout.chartRight}
          y1={layout.chartBottom}
          x2={layout.chartRight - width * 0.01}
          y2={layout.chartBottom + height * 0.015}
          stroke="white"
          strokeWidth={layout.axisStrokeWidth}
        />

        <text
          x={layout.chartRight + width * 0.018}
          y={layout.chartBottom + height * 0.005}
          fill="white"
          fontSize={layout.axisFontSize}
          fontFamily="Madimi One, sans-serif"
          textAnchor="start"
          dominantBaseline="middle"
        >
          release year
        </text>

        <text
          x={layout.chartLeft - width * 0.045}
          y={(layout.chartTop + layout.chartBottom) / 2}
          fill="white"
          fontSize={layout.axisFontSize}
          fontFamily="Madimi One, sans-serif"
          textAnchor="middle"
          dominantBaseline="middle"
          transform={`rotate(-90 ${layout.chartLeft - width * 0.045} ${(layout.chartTop + layout.chartBottom) / 2})`}
        >
          mood intensity
        </text>

        {yearlyMoodAverages.length > 0 && (
          <>
            <text
              x={layout.chartLeft - width * 0.005}
              y={
                layout.chartBottom + layout.roundYearTickHeight + height * 0.04
              }
              fill="white"
              fontSize={layout.axisFontSize}
              fontFamily="Madimi One, sans-serif"
              textAnchor="end"
              dominantBaseline="middle"
            >
              {minYear}
            </text>

            <text
              x={layout.chartRight + width * 0.005}
              y={
                layout.chartBottom + layout.roundYearTickHeight + height * 0.04
              }
              fill="white"
              fontSize={layout.axisFontSize}
              fontFamily="Madimi One, sans-serif"
              textAnchor="start"
              dominantBaseline="middle"
            >
              {maxYear}
            </text>
          </>
        )}

        {MOOD_OPTIONS.map((mood) => {
          if (!enabledMoods[mood]) return null;
          const areaPath = moodPaths[mood]?.areaPath;
          if (!areaPath) return null;

          return (
            <path
              key={`area-${mood}`}
              d={areaPath}
              fill={`url(#line-graph-gradient-${mood})`}
              opacity="0.45"
            />
          );
        })}

        {MOOD_OPTIONS.map((mood) => {
          if (!enabledMoods[mood]) return null;
          const linePath = moodPaths[mood]?.linePath;
          if (!linePath) return null;

          return (
            <path
              key={`line-${mood}`}
              d={linePath}
              fill="none"
              className={moodStrokeClass[mood]}
              strokeWidth={layout.lineStrokeWidth}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          );
        })}
      </svg>

      <div
        className="absolute right-0 top-10 z-10"
        style={{
          width: layout.rightLegendWidth,
          paddingTop: layout.topPadding * 0.9,
          paddingRight: width * 0.02,
        }}
      >
        <div
          className="flex flex-col"
          style={{
            gap: layout.legendRowGap,
          }}
        >
          {MOOD_OPTIONS.map((mood) => (
            <button
              key={mood}
              type="button"
              onClick={() => toggleMood(mood)}
              className="flex items-center justify-start gap-2.5 bg-transparent text-left text-white"
            >
              <span
                className={[
                  "flex shrink-0 items-center justify-center rounded-sm border-[3px]",
                  enabledMoods[mood]
                    ? `${moodBgClass[mood]} ${moodBorderClass[mood]}`
                    : "bg-transparent",
                  moodBorderClass[mood],
                ].join(" ")}
                style={{
                  width: layout.checkboxSize,
                  height: layout.checkboxSize,
                }}
              >
                {enabledMoods[mood] && (
                  <Check
                    size={layout.checkIconSize}
                    className="stroke-dark-blue stroke-[3px]"
                  />
                )}
              </span>

              <span
                className={[
                  "font-madimi leading-none",
                  moodTextClass[mood],
                ].join(" ")}
                style={{
                  fontSize: layout.legendFontSize,
                }}
              >
                {mood}
              </span>
            </button>
          ))}
        </div>
      </div>

      {!songs.length && (
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
          <p
            className="font-madimi text-white/80"
            style={{ fontSize: clamp(Math.min(width, height) * 0.05, 14, 22) }}
          >
            No data for selected filters
          </p>
        </div>
      )}
    </div>
  );
}
