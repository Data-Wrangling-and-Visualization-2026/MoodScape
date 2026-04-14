import { api } from "./axios";

// sends filter data to backend
export async function getFilteredSongs(filters) {
  const params = {
    genre:
      filters.genre && filters.genre !== "all genres"
        ? filters.genre
        : undefined,

    year_from: filters.yearFrom || undefined,
    year_to: filters.yearTo || undefined,

    emotion:
      filters.mainMood && filters.mainMood !== "all moods"
        ? filters.mainMood
        : undefined,

    search: filters.lyrics || undefined,

    limit: 50,
    offset: 0,
    sort_by: "release_date",
    sort_order: "desc",
  };
  
  const { data } = await api.get("tracks/filter/", { params });
  return data;
}

export async function getGenres() {
  const { data } = await api.get("/tracks/genres");
  return data;
}

export async function getYearsRange() {
  const { data } = await api.get("/tracks/years");
  return data;
}