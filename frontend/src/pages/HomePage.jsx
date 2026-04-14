import FiltersPanel from "../components/filters/FiltersPanel";
import ReleaseYearSlider from "../components/slider/ReleaseYearSlider";
import { useSongs } from "../features/songs/useSongs";
import { useFiltersStore } from "../features/filters/filtersStore";

export default function HomePage() {
  const filters = useFiltersStore((state) => state.filters);
  const { data, error, isFetching } = useSongs(filters);

  
  return (
    <div className="h-screen overflow-hidden px-10 py-6">
      <main className="flex h-full flex-col">
        <div className="flex flex-1 justify-end">
          <FiltersPanel />
        </div>

        <div className="shrink-0 text-white">
          {error ? (
            <p>Failed to load songs</p>
          ) : (
            <pre>{data?.length ?? 0}</pre>
          )}

          {/* {isFetching && <p>Updating...</p>} */}
        </div>

        <div className="shrink-0">
          <ReleaseYearSlider />
        </div>
      </main>
    </div>
  );
}