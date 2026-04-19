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
  const total = MOOD_OPTIONS.reduce(
    (sum, mood) => sum + (averages[mood] ?? 0),
    0,
  );

  if (total <= 0) {
    const equalShare = 1 / MOOD_OPTIONS.length;
    return MOOD_OPTIONS.map((mood) => ({
      mood,
      share: equalShare,
    }));
  }

  return MOOD_OPTIONS.map((mood) => ({
    mood,
    share: (averages[mood] ?? 0) / total,
  }));
}

function buildLinearGradient(averages) {
  const shares = buildMoodShares(averages);

  const cumulative = [];
  let acc = 0;

  for (let i = 0; i < shares.length; i += 1) {
    cumulative.push({
      mood: shares[i].mood,
      start: acc * 100,
      share: shares[i].share * 100,
    });
    acc += shares[i].share;
  }

  const stops = [];
  stops.push(`${moodCssVar[cumulative[0].mood]} 0%`);

  for (let i = 0; i < cumulative.length - 1; i += 1) {
    const current = cumulative[i];
    const next = cumulative[i + 1];
    const boundary = current.start + current.share;
    const currentSize = current.share;
    const nextSize = next.share;
    const smallerNeighbor = Math.min(currentSize, nextSize);

    let spread = smallerNeighbor * 0.28;
    spread = clamp(spread, 1.2, 4.8);
    spread = Math.min(spread, currentSize * 0.45, nextSize * 0.45);

    const left = clamp(boundary - spread, 0, 100);
    const right = clamp(boundary + spread, 0, 100);

    if (left > 0) {
      stops.push(`${moodCssVar[current.mood]} ${left.toFixed(3)}%`);
    }

    if (right < 100) {
      stops.push(`${moodCssVar[next.mood]} ${right.toFixed(3)}%`);
    }
  }

  const lastMood = cumulative[cumulative.length - 1].mood;
  stops.push(`${moodCssVar[lastMood]} 100%`);

  return `linear-gradient(to bottom, ${stops.join(", ")})`;
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

export default function HeatmapGraph({
  width,
  height,
  className = "",
}) {
  const filters = useFiltersStore((state) => state.filters);
  const { data } = useSongs(filters);
  const [hoveredBar, setHoveredBar] = useState(null);
  const plotRef = useRef(null);

  const yearlyData = useMemo(() => {
    if (!data?.length) return [];

    return buildYearlyAverages(data).map((entry) => ({
      ...entry,
      gradient: buildLinearGradient(entry.averages),
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
    const legendGap = Math.max(14, safeWidth * 0.02);
    const minPlotWidth = safeWidth * 0.55;

    const axisLabelZone = Math.max(24, safeHeight * 0.06);
    const axisGap = Math.max(12, safeHeight * 0.028);

    const plotX = outerPadLeft + legendWidth;
    const plotY = outerPadTop;

    let plotWidth = safeWidth - plotX - outerPadRight;
    if (plotWidth < minPlotWidth) {
      plotWidth = minPlotWidth;
    }

    const plotHeight =
      safeHeight - outerPadTop - outerPadBottom - axisGap - axisLabelZone;

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
    const legendY = outerPadTop;

    const squareSize = clamp(safeWidth * 0.024, 12, 26);
    const legendRowGap = clamp(safeHeight * 0.012, 6, 12);
    const legendFontSize = clamp(safeWidth * 0.016, 11, 16);

    const yearFontSize = clamp(safeWidth * 0.019, 12, 18);
    const sideYearFontSize = clamp(safeWidth * 0.022, 13, 20);
    const tickLabelFontSize = clamp(safeWidth * 0.014, 10, 13);
    const axisStrokeWidth = clamp(safeHeight * 0.0035, 1.5, 3);
    const tickSize = clamp(safeHeight * 0.02, 5, 8);

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
      yearFontSize,
      sideYearFontSize,
      tickLabelFontSize,
      axisStrokeWidth,
      tickSize,
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
      className={`srelative overflow-hidden ${className}`}
      style={{ width, height }}
    >
      {/* Bars */}
      <div
        ref={plotRef}
        className="absolute"
        style={{
          left: layout.plotX,
          top: layout.plotY,
          width: layout.plotWidth,
          height: layout.plotHeight,
        }}
      >
        {yearlyData.map((item, index) => {
          const left = index * (layout.barWidth + layout.barGap);

          return (
            <div
              key={item.year}
              className="absolute top-0 cursor-pointer"
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
              style={{
                left,
                width: layout.barWidth,
                height: layout.plotHeight,
                backgroundImage: item.gradient,
              }}
            />
          );
        })}

        {hoveredBar && (
          <div
            className="pointer-events-none absolute z-20 rounded-sm bg-white px-2 py-1 text-black shadow-sm"
            style={{
              left: clamp(hoveredBar.x - 50, 4, layout.plotWidth - 60),
              top: clamp(hoveredBar.y - 30, 4, layout.plotHeight - 24),
              fontSize: clamp(layout.safeWidth * 0.014, 10, 13),
              lineHeight: 1,
              whiteSpace: "nowrap",
            }}
          >
            {hoveredBar.year}
          </div>
        )}
      </div>

      {/* Legend */}
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

      {/* Axis and labels */}
      <svg
        className="pointer-events-none absolute inset-0"
        width={layout.safeWidth}
        height={layout.safeHeight}
        viewBox={`0 0 ${layout.safeWidth} ${layout.safeHeight}`}
        fill="none"
      >
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
          y1={layout.axisY - 10}
          x2={layout.plotX + layout.plotWidth + layout.axisOverflow}
          y2={layout.axisY}
          stroke="white"
          strokeWidth={layout.axisStrokeWidth}
        />
        <line
          x1={layout.plotX + layout.plotWidth + layout.axisOverflow - 10}
          y1={layout.axisY + 10}
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
                y={layout.axisY + layout.tickSize + layout.tickLabelFontSize + 2}
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
            x={layout.plotX - layout.axisOverflow - 8}
            y={layout.axisY + layout.sideYearFontSize * 0.35}
            fill="white"
            fontSize={layout.sideYearFontSize}
            fontFamily="var(--font-madimi, inherit)"
            textAnchor="end"
          >
            {minYear}
          </text>
        )}

        {maxYear != null && (
          <text
            x={layout.plotX + layout.plotWidth + layout.axisOverflow + 8}
            y={layout.axisY + layout.sideYearFontSize * 0.35}
            fill="white"
            fontSize={layout.sideYearFontSize}
            fontFamily="var(--font-madimi, inherit)"
            textAnchor="start"
          >
            {maxYear}
          </text>
        )}
      </svg>
    </div>
  );
}