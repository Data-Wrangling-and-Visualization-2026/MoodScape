import { useEffect, useMemo, useRef, useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useFiltersStore } from "../../features/filters/filtersStore";
import { useEvents } from "../../features/events/useEvents";

export default function EventsPanel() {
  const filters = useFiltersStore((state) => state.filters);
  const {
    data: events = [],
    error: errorEvents,
    isFetching: isFetchingEvents,
  } = useEvents(filters);

  const years = useMemo(() => {
    const uniqueYears = [...new Set(events.map((event) => Number(event.year)))];
    return uniqueYears.sort((a, b) => a - b);
  }, [events]);

  const [currentYearIndex, setCurrentYearIndex] = useState(0);

  const scrollRef = useRef(null);

  useEffect(() => {
    setCurrentYearIndex(0);
  }, [years]);

  // 🔥 auto scroll to top when year changes
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0;
    }
  }, [currentYearIndex]);

  const currentYear = years[currentYearIndex];

  const currentYearEvents = useMemo(() => {
    if (!currentYear) return [];
    return events.filter((event) => Number(event.year) === currentYear);
  }, [events, currentYear]);

  const goToPreviousYear = () => {
    setCurrentYearIndex((prev) => Math.max(prev - 1, 0));
  };

  const goToNextYear = () => {
    setCurrentYearIndex((prev) => Math.min(prev + 1, years.length - 1));
  };

  const isLeftDisabled = currentYearIndex === 0;
  const isRightDisabled =
    currentYearIndex === years.length - 1 || years.length === 0;

  return (
    <div className="w-full max-w-[230px]">
      {/* top controls */}
      <div className="mb-4 flex items-center justify-between gap-2 pl-4 pr-4">
        <button
          type="button"
          onClick={goToPreviousYear}
          disabled={isLeftDisabled}
          className={`flex h-8 w-16 items-center justify-center rounded-lg transition ${
            isLeftDisabled
              ? "cursor-not-allowed bg-[#a7a7bb]"
              : "bg-[#7286ff] hover:opacity-90"
          }`}
        >
          <ChevronLeft className="h-5 w-5 text-white" />
        </button>

        <p className="min-w-[60px] text-center font-madimi text-2xl text-white">
          {currentYear ?? "—"}
        </p>

        <button
          type="button"
          onClick={goToNextYear}
          disabled={isRightDisabled}
          className={`flex h-8 w-16 items-center justify-center rounded-lg transition ${
            isRightDisabled
              ? "cursor-not-allowed bg-[#a7a7bb]"
              : "bg-[#7286ff] hover:opacity-90"
          }`}
        >
          <ChevronRight className="h-5 w-5 text-white" />
        </button>
      </div>

      {/* scrollable event box */}
      <div
        ref={scrollRef}
        className="custom-scrollbar h-[250px] overflow-y-auto rounded-r-lg rounded-l-none bg-white p-4 shadow-md"
      >
        {isFetchingEvents ? (
          <p className="font-afacad text-base text-slate-700">
            Loading events...
          </p>
        ) : errorEvents ? (
          <p className="font-afacad text-base text-red-600">
            Failed to load events.
          </p>
        ) : currentYearEvents.length === 0 ? (
          <p className="font-afacad text-base text-slate-700">
            No important events for this year.
          </p>
        ) : (
          <div className="flex flex-col space-y-6">
            {currentYearEvents.map((event, index) => (
              <div key={`${event.year}-${event.event_name}-${index}`}>
                <h3 className="mb-1 font-madimi text-lg leading-tight text-black">
                  {index + 1}. {event.event_name}
                </h3>

                <p className="font-afacad text-sm leading-snug text-black">
                  {event.description}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}