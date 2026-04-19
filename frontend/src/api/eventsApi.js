import { api } from "./axios";

export async function getEvents(filters) {
  const params = {
    year_from: filters.yearFrom || undefined,
    year_to: filters.yearTo || undefined,
  };

  const { data } = await api.get("/events/range", { params });
  return data;
}
