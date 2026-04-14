import { useEffect, useMemo, useState } from "react";
import { useYearsRange } from "../../features/songs/useYearsRange";
import { useFiltersStore } from "../../features/filters/filtersStore";

export default function ReleaseYearSlider() {
    // getting the range of years from bd
    const { data: years = [], isLoading, error } = useYearsRange();

    // current filters state and function for adding year range to filters
    const filters = useFiltersStore((state) => state.filters);
    const setYearRange = useFiltersStore((state) => state.setYearRange);

    // useMemo: recalculates the minYear maxYear only if years returned change
    const { minYear, maxYear } = useMemo(() => {
        // gives default values if bd returned no years
        if (!years.length) {
            return { minYear: 1900, maxYear: 2026 };
        }

        // gives the min and max year from the bd response
        return {
            minYear: Math.min(...years),
            maxYear: Math.max(...years),
        };
    }, [years]);

    const [leftYear, setLeftYear] = useState(minYear);
    const [rightYear, setRightYear] = useState(maxYear);

    // whenether dependencies change, recalculate the slider year values
    useEffect(() => {
        const rawLeft = filters.yearFrom ?? minYear;
        const rawRight = filters.yearTo ?? maxYear;

        // prevents slider from going out of range
        const initialLeft = Math.max(minYear, Math.min(rawLeft, maxYear));
        const initialRight = Math.min(maxYear, Math.max(rawRight, minYear));

        setLeftYear(initialLeft);
        setRightYear(initialRight);
    }, [filters.yearFrom, filters.yearTo, minYear, maxYear]);

    
    // applies filters when the slider is dragged
    useEffect(() => {
        setYearRange(leftYear, rightYear);
    }, [leftYear, rightYear, setYearRange]);

    // calculating the relative positions for slider handles
    // and year descriptions under them
    const range = maxYear - minYear || 1;
    const leftPercent = ((leftYear - minYear) / range) * 100;
    const rightPercent = ((rightYear - minYear) / range) * 100;

    if (isLoading) return <p>Loading years...</p>;
    if (error) return <p>Failed to load years</p>;

    return (
        <section className="mt-8 flex w-full justify-center text-white">
            <div className="flex w-full max-w-5xl flex-col items-center">
            <h2 className="mb-3 text-center font-afacad text-4xl">
                year of release
            </h2>

            <div className="flex w-full items-start gap-4 font-madimi text-2xl">
                <span className="pt-1">{minYear}</span>

                <div className="flex flex-1 flex-col">
                <div className="relative h-10">
                    <div className="absolute top-1/2 h-4 w-full -translate-y-1/2 rounded-full bg-blue-pastel" />

                    <div
                    className="absolute top-1/2 h-4 -translate-y-1/2 rounded-full bg-green-pastel"
                    style={{
                        left: `${leftPercent}%`,
                        width: `${rightPercent - leftPercent}%`,
                    }}
                    />

                    <input
                    type="range"
                    min={minYear}
                    max={maxYear}
                    step={1}
                    value={leftYear}
                    onChange={(e) =>
                        setLeftYear(Math.min(Number(e.target.value), rightYear - 1))
                    }
                    className="dual-range dual-range-left"
                    />

                    <input
                    type="range"
                    min={minYear}
                    max={maxYear}
                    step={1}
                    value={rightYear}
                    onChange={(e) =>
                        setRightYear(Math.max(Number(e.target.value), leftYear + 1))
                    }
                    className="dual-range dual-range-right"
                    />
                </div>

                <div className="relative mt-3 h-8">
                    <span
                    className="absolute -translate-x-1/2 font-madimi text-2xl text-white"
                    style={{ left: `${leftPercent}%` }}
                    >
                    {leftYear}
                    </span>

                    <span
                    className="absolute -translate-x-1/2 font-madimi text-2xl text-white"
                    style={{ left: `${rightPercent}%` }}
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