import { useEffect, useMemo, useRef, useState } from "react";
import { useYearsRange } from "../../features/songs/useYearsRange";
import { useFiltersStore } from "../../features/filters/filtersStore";

export default function ReleaseYearSlider() {
  const { data: years = [], isLoading, error } = useYearsRange();

  const filters = useFiltersStore((state) => state.filters);
  const setYearRange = useFiltersStore((state) => state.setYearRange);

  const trackRef = useRef(null);

  const { minYear, maxYear } = useMemo(() => {
    if (!years.length) {
      return { minYear: 1900, maxYear: 2026 };
    }

    return {
      minYear: Math.min(...years),
      maxYear: Math.max(...years),
    };
  }, [years]);

  const [leftYear, setLeftYear] = useState(filters.yearFrom ?? minYear);
  const [rightYear, setRightYear] = useState(filters.yearTo ?? maxYear);

  const [dragging, setDragging] = useState(null); // "left" | "right" | null
  const [dragStartX, setDragStartX] = useState(null);

  const isCustomDragging = dragStartX !== null;

  useEffect(() => {
  if (!years.length) return;

  const nextLeft = filters.yearFrom ?? minYear;
  const nextRight = filters.yearTo ?? maxYear;

  setLeftYear(Math.max(minYear, Math.min(nextLeft, maxYear)));
  setRightYear(Math.min(maxYear, Math.max(nextRight, minYear)));
  setYearRange(
    Math.max(minYear, Math.min(nextLeft, maxYear)),
    Math.min(maxYear, Math.max(nextRight, minYear))
  );
}, [years, minYear, maxYear, filters.yearFrom, filters.yearTo, setYearRange]);


  const range = maxYear - minYear || 1;
  const leftPercent = ((leftYear - minYear) / range) * 100;
  const rightPercent = ((rightYear - minYear) / range) * 100;
  const isOverlapping = leftYear === rightYear;

  function positionToYear(clientX) {
    const rect = trackRef.current?.getBoundingClientRect();
    if (!rect) return minYear;

    const ratio = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
    const rawYear = minYear + ratio * (maxYear - minYear);
    return Math.round(rawYear);
  }

  function handlePointerDown(e) {
    if (!isOverlapping) return;
    setDragStartX(e.clientX);
    setDragging(null);
  }

  function handlePointerMove(e) {
    if (dragStartX === null) return;

    let active = dragging;

    if (!active) {
      const dx = e.clientX - dragStartX;

      // ignore tiny accidental movement
      if (Math.abs(dx) < 4) return;

      active = dx < 0 ? "left" : "right";
      setDragging(active);
    }

    const year = positionToYear(e.clientX);

    if (active === "left") {
      setLeftYear(Math.min(year, rightYear));
    } else if (active === "right") {
      setRightYear(Math.max(year, leftYear));
    }
  }

  function handlePointerUp() {
    setDragging(null);
    setDragStartX(null);
    setYearRange(leftYear, rightYear);
  }

  if (isLoading) return <p>Loading years...</p>;
  if (error) return <p>Failed to load years</p>;

  return (
    <section className="mt-4 flex w-full justify-center text-white">
      <div className="flex w-full max-w-3xl flex-col items-center">
        <h2 className="text-center font-afacad text-2xl">
          year of release
        </h2>

        <div className="flex w-full items-start gap-4 font-madimi text-2xl">
          <span className="pt-1">{minYear}</span>

          <div className="flex flex-1 flex-col">
            <div
              ref={trackRef}
              className="relative h-10"
              onPointerDown={handlePointerDown}
              onPointerMove={handlePointerMove}
              onPointerUp={handlePointerUp}
              onPointerLeave={handlePointerUp}
            >
              <div className="absolute top-1/2 h-4 w-full -translate-y-1/2 rounded-full bg-blue-pastel" />

              <div
                className="absolute top-1/2 h-4 -translate-y-1/2 rounded-full bg-green-pastel"
                style={{
                  left: `${leftPercent}%`,
                  width: `${Math.max(rightPercent - leftPercent, 0)}%`,
                }}
              />

              <input
                type="range"
                min={minYear}
                max={maxYear}
                step={1}
                value={leftYear}
                onChange={(e) => {
                  if (isCustomDragging) return;
                  setLeftYear(Math.min(Number(e.target.value), rightYear));
                }}
                onMouseUp={() => setYearRange(leftYear, rightYear)}
                onTouchEnd={() => setYearRange(leftYear, rightYear)}
                onKeyUp={() => setYearRange(leftYear, rightYear)}
                className={`dual-range ${dragging === "left" ? "z-30" : "z-20"}`}
              />

              <input
                type="range"
                min={minYear}
                max={maxYear}
                step={1}
                value={rightYear}
                onChange={(e) => {
                  if (isCustomDragging) return;
                  setRightYear(Math.max(Number(e.target.value), leftYear));
                }}
                onMouseUp={() => setYearRange(leftYear, rightYear)}
                onTouchEnd={() => setYearRange(leftYear, rightYear)}
                onKeyUp={() => setYearRange(leftYear, rightYear)}
                className={`dual-range ${dragging === "right" ? "z-30" : "z-10"}`}
              />
            </div>

            <div className="relative mt-3 h-8">
              <span
                className="absolute font-madimi text-xl text-white"
                style={{
                  left: `${leftPercent}%`,
                  transform:
                    leftYear !== rightYear
                      ? "translateX(-90%)"
                      : "translateX(-50%)",
                }}
              >
                {leftYear}
              </span>

              <span
                className="absolute font-madimi text-xl text-white"
                style={{
                  left: `${rightPercent}%`,
                  transform:
                    leftYear !== rightYear
                      ? "translateX(-10%)"
                      : "translateX(-50%)",
                }}
              >
                {rightYear}
              </span>
            </div>
          </div>

          <span className="pt-1">{maxYear}</span>
        </div>
      </div>
    </section>
  );
}