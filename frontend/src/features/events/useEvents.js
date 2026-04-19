import { useQuery } from "@tanstack/react-query";
import { getEvents } from "../../api/eventsApi";


export function useEvents(filters = {}) {
  return useQuery({
    queryKey: ["events", filters.yearFrom, filters.yearTo],
    queryFn: () =>
      getEvents({
        yearFrom: filters.yearFrom,
        yearTo: filters.yearTo,
      }),
    enabled: filters.yearFrom != null && filters.yearTo != null,
  });
}