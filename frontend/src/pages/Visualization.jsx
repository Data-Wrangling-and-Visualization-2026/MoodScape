import FiltersPanel from "../components/filters/FiltersPanel";
import EventsPanel from "../components/events/EventsPanel";
import ReleaseYearSlider from "../components/slider/ReleaseYearSlider";
import { useSongs } from "../features/songs/useSongs";
import { useEvents } from "../features/events/useEvents";
import { useFiltersStore } from "../features/filters/filtersStore";
import GraphTabsBox from "../components/graphs/GraphTabsBox";

export default function Visualization() {
  const filters = useFiltersStore((state) => state.filters);
  const { data, error, isFetching } = useSongs(filters);
  const {
    data: events,
    error: errorEvents,
    isFetching: isFetchingEvents,
  } = useEvents(filters);

  return (
    <div className="relative h-screen overflow-hidden pr-5 pt-3 pb-3">
      {/* TOP TEXTS */}
      <div className="pointer-events-none absolute left-0 top-3 w-full">
        <p className="text-center font-afacad text-lg text-white">
          discover the mood of the most popular songs in Russia!
        </p>

        <p className="absolute left-5 top-0 font-madimi text-4xl text-white">
          moodscape
        </p>
      </div>

      <main className="flex h-full flex-col">
        <section className="grid min-h-0 flex-1 grid-cols-[240px_1fr_220px] gap-6 ">
          {/* LEFT SIDE */}
          <aside className="flex min-h-0 flex-col items-start pt-20">
            <EventsPanel />

            <div className="mt-4 ml-4 w-full max-w-[170px] relative">
              <p className="text-left font-afacad text-xl leading-snug text-white">
                see important events of the selected period
              </p>

              {/* arrow */}
              <svg
                className="absolute right-0 top-0 translate-x-10 -translate-y-6"
                width="80"
                height="80"
                viewBox="0 0 100 100"
                fill="none"
              >
                <path
                  d="M20 85 Q 70 80 80 30"
                  stroke="white"
                  strokeWidth="4"
                  strokeLinecap="round"
                />
                <path
                  d="M80 30 L65 35 M80 30 L90 40"
                  stroke="white"
                  strokeWidth="4"
                  strokeLinecap="round"
                />
              </svg>
            </div>
          </aside>

          {/* CENTER */}
          <section className="min-h-0 pt-10">
            <GraphTabsBox />
          </section>

          {/* RIGHT */}
          <aside className="flex min-h-0 flex-col items-center mt-[50px] gap-3 pt-20">
            <FiltersPanel />

            <img src="/meymuni.gif" alt="smol monke" className="w-20 h-auto" />
          </aside>
        </section>

        {/* SLIDER */}
        <section className="mt-auto flex justify-center pt-6">
          <div className="w-full max-w-4xl">
            <ReleaseYearSlider />
          </div>
        </section>
      </main>
    </div>
  );
}
