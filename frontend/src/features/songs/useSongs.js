import { useQuery } from "@tanstack/react-query";
import { getFilteredSongs } from "../../api/songsApi";

// enables caching filters
// automatic refresh when filters change
// handles requests to backend
export function useSongs(filters) {
  return useQuery({
    queryKey: ["filtered-songs", filters],
    queryFn: () => getFilteredSongs(filters),
  });
}