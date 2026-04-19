import { useQuery } from "@tanstack/react-query";
import { getYearsRange } from "../../api/songsApi";

export function useYearsRange() {
  return useQuery({
    queryKey: ["years"],
    queryFn: getYearsRange,
  });
}
