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
  const [isEditingYear, setIsEditingYear] = useState(false);
  const [yearInput, setYearInput] = useState("");
  const [warning, setWarning] = useState("");

  const scrollRef = useRef(null);
  const yearInputRef = useRef(null);

  useEffect(() => {
    setCurrentYearIndex(0);
  }, [years]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0;
    }
  }, [currentYearIndex]);

  const currentYear = years[currentYearIndex];
  const minYear = years.length ? years[0] : undefined;
  const maxYear = years.length ? years[years.length - 1] : undefined;

  useEffect(() => {
    if (!isEditingYear) {
      setYearInput(currentYear != null ? String(currentYear) : "");
    }
  }, [currentYear, isEditingYear]);

  useEffect(() => {
    if (isEditingYear && yearInputRef.current) {
      yearInputRef.current.focus();
      yearInputRef.current.select();
    }
  }, [isEditingYear]);

  const currentYearEvents = useMemo(() => {
    if (!currentYear) return [];
    return events.filter((event) => Number(event.year) === currentYear);
  }, [events, currentYear]);

  const goToPreviousYear = () => {
    setWarning("");
    setCurrentYearIndex((prev) => Math.max(prev - 1, 0));
  };

  const goToNextYear = () => {
    setWarning("");
    setCurrentYearIndex((prev) => Math.min(prev + 1, years.length - 1));
  };

  const startEditingYear = () => {
    if (!years.length) return;
    setWarning("");
    setYearInput(String(currentYear));
    setIsEditingYear(true);
  };

  const cancelEditingYear = () => {
    setYearInput(currentYear != null ? String(currentYear) : "");
    setIsEditingYear(false);
  };

  const confirmYearInput = () => {
    if (!years.length) {
      setIsEditingYear(false);
      return;
    }

    const parsedYear = Number(yearInput);

    if (
      yearInput.trim() === "" ||
      Number.isNaN(parsedYear) ||
      parsedYear < minYear ||
      parsedYear > maxYear
    ) {
      setWarning(`Please enter a year from ${minYear} to ${maxYear}.`);
      setYearInput(String(currentYear));
      setIsEditingYear(false);
      return;
    }

    const matchedIndex = years.findIndex((year) => year === parsedYear);

    if (matchedIndex === -1) {
      setWarning(
        `No events exist for ${parsedYear}. Returning to ${currentYear}.`,
      );
      setYearInput(String(currentYear));
      setIsEditingYear(false);
      return;
    }

    setWarning("");
    setCurrentYearIndex(matchedIndex);
    setIsEditingYear(false);
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

        {isEditingYear ? (
          <input
            ref={yearInputRef}
            type="text"
            value={yearInput}
            onChange={(e) => {
              const digitsOnly = e.target.value.replace(/\D/g, "");
              setYearInput(digitsOnly);
            }}
            onBlur={confirmYearInput}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                confirmYearInput();
              }
              if (e.key === "Escape") {
                cancelEditingYear();
              }
            }}
            className="min-w-[60px] border-none bg-transparent text-center font-madimi text-2xl text-white outline-none"
          />
        ) : (
          <button
            type="button"
            onClick={startEditingYear}
            className="min-w-[60px] text-center font-madimi text-2xl text-white"
          >
            {currentYear ?? "—"}
          </button>
        )}

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

      {warning ? (
        <p className="mb-2 px-4 font-afacad text-sm leading-snug text-yellow-300">
          {warning}
        </p>
      ) : null}

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
