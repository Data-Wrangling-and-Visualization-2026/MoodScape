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

  if (isLoading) return <p>Loading filters...</p>;
  if (error) return <p>Failed to load filters</p>;

  return (
    <form
        onSubmit={handleSubmit(onSubmit)}
        className="flex w-[230px] flex-col gap-4"
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
            className="h-30 w-full rounded-xl bg-zinc-100 px-5 pr-5 text-2xl font-black text-black outline-none placeholder:text-zinc-500"
        />

        <Search strokeWidth={4} className="absolute bottom-3 right-4 h-6 w-6 text-black" />
        </div>

        <button
        type="submit"
        className="h-12 rounded-2xl bg-indigo-500 text-2xl font-black text-white shadow-md transition hover:opacity-90"
        >
        Apply filters!
        </button>
    </form>
    );
}