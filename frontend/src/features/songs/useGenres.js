import { useQuery } from "@tanstack/react-query";
import { getGenres } from "../../api/songsApi";

export function useGenres() {
  return useQuery({
    queryKey: ["genres"],
    queryFn: getGenres,
  });
}
