import { useForm, Controller } from "react-hook-form";
import { useGenres } from "../../features/songs/useGenres";
import { useFiltersStore } from "../../features/filters/filtersStore";
import { MOOD_OPTIONS } from "../../features/filters/moodOptions";
import Dropdown from "../ui/Dropdown";
import { Search } from "lucide-react";

export default function FiltersPanel() {
  const { data: genres = [], isLoading, error } = useGenres();

  const filters = useFiltersStore((state) => state.filters);
  const setFilters = useFiltersStore((state) => state.setFilters);

  const { register, handleSubmit, control } = useForm({
    defaultValues: {
      genre: filters.genre,
      mainMood: filters.mainMood,
      lyrics: filters.lyrics,
    },
  });

  const onSubmit = (formData) => {
    setFilters({
      ...filters,
      genre: formData.genre,
      mainMood: formData.mainMood,
      lyrics: formData.lyrics,
    });
  };

  if (isLoading) {
    return <p className="font-afacad text-white">Loading filters...</p>;
  }

  if (error) {
    return <p className="font-afacad text-white">Failed to load filters</p>;
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="flex w-full max-w-[200px] flex-col gap-3"
    >
      <Controller
        name="genre"
        control={control}
        render={({ field }) => (
          <Dropdown
            options={["all genres", ...genres]}
            value={field.value}
            onChange={field.onChange}
            placeholder="genre"
          />
        )}
      />

      <Controller
        name="mainMood"
        control={control}
        render={({ field }) => (
          <Dropdown
            options={["all moods", ...MOOD_OPTIONS]}
            value={field.value}
            onChange={field.onChange}
            placeholder="main mood"
          />
        )}
      />

      <div className="relative">
        <input
          type="text"
          placeholder="search by lyrics"
          {...register("lyrics")}
          className="h-25 w-full rounded-lg bg-zinc-100 px-4 pr-10 text-lg font-black text-black outline-none placeholder:text-zinc-500"
        />

        <Search
          strokeWidth={3}
          className="absolute bottom-5 right-3 h-5 w-5 text-black"
        />
      </div>

      <button
        type="submit"
        className="h-11 rounded-lg bg-indigo-500 text-base font-black text-white shadow-md transition hover:opacity-90"
      >
        Apply filters!
      </button>
    </form>
  );
}
