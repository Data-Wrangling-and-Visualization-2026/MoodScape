import { useMemo, useRef, useState } from "react";
import { useFiltersStore } from "../../features/filters/filtersStore";
import { useSongs } from "../../features/songs/useSongs";
import { MOOD_OPTIONS } from "../../features/filters/moodOptions";
import { moodTextClass } from "../../features/graphs/moodTextColours";

const moodCssVar = {
  anger: "var(--color-red-pastel)",
  anticipation: "var(--color-orange-pastel)",
  happiness: "var(--color-yellow-pastel)",
  disgust: "var(--color-green-pastel)",
  sadness: "var(--color-blue-pastel)",
  fear: "var(--color-purple-pastel)",
};

const moodBgClass = {
  anger: "bg-red-pastel",
  anticipation: "bg-orange-pastel",
  happiness: "bg-yellow-pastel",
  disgust: "bg-green-pastel",
  sadness: "bg-blue-pastel",
  fear: "bg-purple-pastel",
};

function clamp(value, min, max) {
  return Math.max(min, Math.min(value, max));
}

function buildYearlyAverages(data) {
  const byYear = new Map();

  data.forEach((song) => {
    const year = Number(song.year);
    if (!Number.isFinite(year)) return;

    if (!byYear.has(year)) {
      byYear.set(year, {
        year,
        songCount: 0,
        sums: Object.fromEntries(MOOD_OPTIONS.map((mood) => [mood, 0])),
      });
    }

    const bucket = byYear.get(year);
    bucket.songCount += 1;

    const components = Array.isArray(song.emotion_components)
      ? song.emotion_components
      : [];

    components.forEach((item) => {
      const emotion = item?.emotion;
      const weight = Number(item?.weight);

      if (!MOOD_OPTIONS.includes(emotion)) return;
      if (!Number.isFinite(weight)) return;

      bucket.sums[emotion] += clamp(weight, 0, 10);
    });
  });

  return Array.from(byYear.values())
    .sort((a, b) => a.year - b.year)
    .map((entry) => {
      const averages = {};

      MOOD_OPTIONS.forEach((mood) => {
        averages[mood] =
          entry.songCount > 0 ? entry.sums[mood] / entry.songCount : 0;
      });

      return {
        year: entry.year,
        songCount: entry.songCount,
        averages,
      };
    });
}

function buildMoodShares(averages) {
  const rawShares = MOOD_OPTIONS.map((mood) => ({
    mood,
    value: Math.max(0, Number(averages[mood] ?? 0)),
  }));

  const total = rawShares.reduce((sum, item) => sum + item.value, 0);

  if (total <= 0) {
    const equalShare = 1 / MOOD_OPTIONS.length;
    return MOOD_OPTIONS.map((mood) => ({
      mood,
      share: equalShare,
    }));
  }

  return rawShares
    .filter((item) => item.value > 0.00001)
    .map((item) => ({
      mood: item.mood,
      share: item.value / total,
    }));
}

function buildGradientStops(averages) {
  const shares = buildMoodShares(averages);

  if (!shares.length) {
    return [
      { offset: 0, color: moodCssVar[MOOD_OPTIONS[0]] },
      { offset: 100, color: moodCssVar[MOOD_OPTIONS[0]] },
    ];
  }

  if (shares.length === 1) {
    return [
      { offset: 0, color: moodCssVar[shares[0].mood] },
      { offset: 100, color: moodCssVar[shares[0].mood] },
    ];
  }

  const segments = [];
  let acc = 0;

  for (let i = 0; i < shares.length; i += 1) {
    const start = acc * 100;
    const share = shares[i].share * 100;
    const end = start + share;

    segments.push({
      mood: shares[i].mood,
      start,
      share,
      end,
    });

    acc += shares[i].share;
  }

  const stops = [{ offset: 0, color: moodCssVar[segments[0].mood] }];

  for (let i = 0; i < segments.length - 1; i += 1) {
    const current = segments[i];
    const next = segments[i + 1];
    const boundary = current.end;
    const smallerNeighbor = Math.min(current.share, next.share);

    const desiredSpread = clamp(smallerNeighbor * 0.3, 1.4, 5.6);
    const maxAllowedSpread = Math.min(current.share * 0.48, next.share * 0.48);
    const spread = Math.max(0.08, Math.min(desiredSpread, maxAllowedSpread));

    const left = clamp(boundary - spread, 0, 100);
    const right = clamp(boundary + spread, 0, 100);

    if (left > stops[stops.length - 1].offset) {
      stops.push({ offset: left, color: moodCssVar[current.mood] });
    }

    if (right > left) {
      stops.push({ offset: right, color: moodCssVar[next.mood] });
    }
  }

  stops.push({
    offset: 100,
    color: moodCssVar[segments[segments.length - 1].mood],
  });

  return stops;
}

function getRoundYears(minYear, maxYear) {
  if (!Number.isFinite(minYear) || !Number.isFinite(maxYear)) return [];

  const start = Math.ceil(minYear / 10) * 10;
  const years = [];

  for (let year = start; year <= maxYear; year += 10) {
    years.push(year);
  }

  return years;
}

export default function HeatmapGraph({ width, height, className = "" }) {
  const filters = useFiltersStore((state) => state.filters);
  const { data } = useSongs(filters);
  const [hoveredBar, setHoveredBar] = useState(null);
  const plotRef = useRef(null);

  const yearlyData = useMemo(() => {
    if (!data?.length) return [];

    return buildYearlyAverages(data).map((entry) => ({
      ...entry,
      stops: buildGradientStops(entry.averages),
    }));
  }, [data]);

  const yearsCount = yearlyData.length;
  const minYear = yearlyData[0]?.year;
  const maxYear = yearlyData[yearlyData.length - 1]?.year;

  const layout = useMemo(() => {
    const safeWidth = Math.max(320, width || 800);
    const safeHeight = Math.max(220, height || 400);

    const outerPadLeft = safeWidth * 0.04;
    const outerPadRight = safeWidth * 0.1;
    const outerPadTop = safeHeight * 0.15;
    const outerPadBottom = safeHeight * 0.09;

    const legendWidth = Math.min(safeWidth * 0.18, 160);
    const minPlotWidth = safeWidth * 0.55;

    const axisLabelZone = Math.max(24, safeHeight * 0.06);
    const axisGap = Math.max(12, safeHeight * 0.028);
    const titleZone = Math.max(26, safeHeight * 0.07);

    const plotX = outerPadLeft + legendWidth;
    const plotY = outerPadTop + titleZone;

    let plotWidth = safeWidth - plotX - outerPadRight;
    if (plotWidth < minPlotWidth) {
      plotWidth = minPlotWidth;
    }

    const plotHeight =
      safeHeight - plotY - outerPadBottom - axisGap - axisLabelZone;

    const minBarGap = 4;
    const maxBarGap = 14;

    let barGap = 0;
    let barWidth = 0;

    if (yearsCount > 0) {
      const estimatedGap = plotWidth * 0.008;
      barGap = clamp(estimatedGap, minBarGap, maxBarGap);

      const totalGap = barGap * Math.max(0, yearsCount - 1);
      barWidth = (plotWidth - totalGap) / yearsCount;

      if (barWidth < 3) {
        barGap = Math.max(1, Math.floor(plotWidth * 0.003));
        const retryTotalGap = barGap * Math.max(0, yearsCount - 1);
        barWidth = (plotWidth - retryTotalGap) / yearsCount;
      }

      barWidth = Math.max(1, barWidth);
    }

    const axisY = plotY + plotHeight + axisGap;
    const axisOverflow = clamp(plotWidth * 0.03, 10, 22);

    const legendX = outerPadLeft;
    const legendY = plotY;

    const squareSize = clamp(safeWidth * 0.024, 12, 26);
    const legendRowGap = clamp(safeHeight * 0.012, 6, 12);
    const legendFontSize = clamp(safeWidth * 0.016, 11, 16);

    const sideYearFontSize = clamp(safeWidth * 0.022, 13, 20);
    const tickLabelFontSize = clamp(safeWidth * 0.014, 10, 13);
    const axisStrokeWidth = clamp(safeHeight * 0.0035, 1.5, 3);
    const tickSize = clamp(safeHeight * 0.02, 5, 8);
    const titleFontSize = clamp(safeWidth * 0.022, 14, 22);
    const axisNameFontSize = clamp(safeWidth * 0.017, 11, 17);

    return {
      safeWidth,
      safeHeight,
      plotX,
      plotY,
      plotWidth,
      plotHeight,
      barWidth,
      barGap,
      axisY,
      axisOverflow,
      legendX,
      legendY,
      legendWidth,
      squareSize,
      legendRowGap,
      legendFontSize,
      sideYearFontSize,
      tickLabelFontSize,
      axisStrokeWidth,
      tickSize,
      titleFontSize,
      axisNameFontSize,
      titleZone,
    };
  }, [width, height, yearsCount]);

  const roundYears = useMemo(
    () => getRoundYears(minYear, maxYear),
    [minYear, maxYear],
  );

  function getYearX(year) {
    if (
      !Number.isFinite(year) ||
      !Number.isFinite(minYear) ||
      !Number.isFinite(maxYear)
    ) {
      return layout.plotX;
    }

    if (maxYear === minYear) {
      return layout.plotX + layout.plotWidth / 2;
    }

    const ratio = (year - minYear) / (maxYear - minYear);
    return layout.plotX + ratio * layout.plotWidth;
  }

  return (
    <div
      className={`relative overflow-hidden ${className}`}
      style={{ width, height }}
    >
      <svg
        ref={plotRef}
        className="absolute inset-0"
        width={layout.safeWidth}
        height={layout.safeHeight}
        viewBox={`0 0 ${layout.safeWidth} ${layout.safeHeight}`}
        fill="none"
      >
        <defs>
          {yearlyData.map((item) => (
            <linearGradient
              key={`gradient-${item.year}`}
              id={`heatmap-gradient-${item.year}`}
              x1="0%"
              y1="0%"
              x2="0%"
              y2="100%"
            >
              {item.stops.map((stop, index) => (
                <stop
                  key={`${item.year}-${index}-${stop.offset}-${stop.color}`}
                  offset={`${stop.offset}%`}
                  stopColor={stop.color}
                />
              ))}
            </linearGradient>
          ))}
        </defs>

        <text
          x={layout.plotX + layout.plotWidth / 2}
          y={layout.plotY - layout.titleZone * 0.45}
          fill="white"
          fontSize={layout.titleFontSize}
          fontFamily="var(--font-madimi, inherit)"
          textAnchor="middle"
        >
          Average mood share by year
        </text>

        {yearlyData.map((item, index) => {
          const x = layout.plotX + index * (layout.barWidth + layout.barGap);

          return (
            <rect
              key={item.year}
              x={x}
              y={layout.plotY}
              width={layout.barWidth}
              height={layout.plotHeight}
              fill={`url(#heatmap-gradient-${item.year})`}
              style={{ cursor: "pointer" }}
              onMouseEnter={(e) => {
                const rect = plotRef.current?.getBoundingClientRect();
                if (!rect) return;

                setHoveredBar({
                  year: item.year,
                  x: e.clientX - rect.left,
                  y: e.clientY - rect.top,
                });
              }}
              onMouseMove={(e) => {
                const rect = plotRef.current?.getBoundingClientRect();
                if (!rect) return;

                setHoveredBar({
                  year: item.year,
                  x: e.clientX - rect.left,
                  y: e.clientY - rect.top,
                });
              }}
              onMouseLeave={() => setHoveredBar(null)}
            />
          );
        })}

        <line
          x1={layout.plotX - layout.axisOverflow}
          y1={layout.axisY}
          x2={layout.plotX + layout.plotWidth + layout.axisOverflow}
          y2={layout.axisY}
          stroke="white"
          strokeWidth={layout.axisStrokeWidth}
        />

        <line
          x1={layout.plotX + layout.plotWidth + layout.axisOverflow - 10}
          y1={layout.axisY - 5}
          x2={layout.plotX + layout.plotWidth + layout.axisOverflow}
          y2={layout.axisY}
          stroke="white"
          strokeWidth={layout.axisStrokeWidth}
        />
        <line
          x1={layout.plotX + layout.plotWidth + layout.axisOverflow - 10}
          y1={layout.axisY + 5}
          x2={layout.plotX + layout.plotWidth + layout.axisOverflow}
          y2={layout.axisY}
          stroke="white"
          strokeWidth={layout.axisStrokeWidth}
        />

        {roundYears.map((year) => {
          const x = getYearX(year);

          return (
            <g key={year}>
              <line
                x1={x}
                y1={layout.axisY - layout.tickSize / 2}
                x2={x}
                y2={layout.axisY + layout.tickSize / 2}
                stroke="white"
                strokeOpacity="0.45"
                strokeWidth={Math.max(1, layout.axisStrokeWidth * 0.8)}
              />
              <text
                x={x}
                y={
                  layout.axisY + layout.tickSize + layout.tickLabelFontSize + 2
                }
                fill="white"
                fillOpacity="0.35"
                fontSize={layout.tickLabelFontSize}
                fontFamily="var(--font-madimi, inherit)"
                textAnchor="middle"
              >
                {year}
              </text>
            </g>
          );
        })}

        {minYear != null && (
          <text
            x={layout.plotX - layout.axisOverflow + 25}
            y={layout.axisY + layout.tickSize + layout.tickLabelFontSize + 2}
            fill="white"
            fontSize={layout.tickLabelFontSize}
            fontFamily="var(--font-madimi, inherit)"
            textAnchor="end"
          >
            {minYear}
          </text>
        )}

        {maxYear != null && (
          <text
            x={layout.plotX + layout.plotWidth + layout.axisOverflow - 25}
            y={layout.axisY + layout.tickSize + layout.tickLabelFontSize + 2}
            fill="white"
            fontSize={layout.tickLabelFontSize}
            fontFamily="var(--font-madimi, inherit)"
            textAnchor="start"
          >
            {maxYear}
          </text>
        )}

        <text
          x={layout.plotX - layout.axisOverflow - 75}
          y={layout.axisY + layout.tickLabelFontSize * 0.35}
          fill="white"
          fontSize={layout.axisNameFontSize}
          fontFamily="var(--font-madimi, inherit)"
          textAnchor="start"
        >
          release year
        </text>
      </svg>

      {hoveredBar && (
        <div
          className="pointer-events-none absolute z-20 rounded-sm bg-white px-2 py-1 text-black shadow-sm"
          style={{
            left: clamp(hoveredBar.x - 50, 4, layout.safeWidth - 60),
            top: clamp(hoveredBar.y - 30, 4, layout.safeHeight - 24),
            fontSize: clamp(layout.safeWidth * 0.014, 10, 13),
            lineHeight: 1,
            whiteSpace: "nowrap",
          }}
        >
          {hoveredBar.year}
        </div>
      )}

      <div
        className="absolute"
        style={{
          left: layout.legendX,
          top: layout.legendY,
          width: layout.legendWidth,
        }}
      >
        <div className="flex flex-col">
          {MOOD_OPTIONS.map((mood) => (
            <div
              key={mood}
              className="flex items-center"
              style={{
                marginBottom: layout.legendRowGap,
                gap: Math.max(7, layout.squareSize * 0.42),
              }}
            >
              <div
                className={`shrink-0 ${moodBgClass[mood]}`}
                style={{
                  width: layout.squareSize,
                  height: layout.squareSize,
                }}
              />
              <span
                className={`font-madimi ${moodTextClass[mood]}`}
                style={{
                  fontSize: layout.legendFontSize,
                  lineHeight: 1,
                }}
              >
                {mood}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
