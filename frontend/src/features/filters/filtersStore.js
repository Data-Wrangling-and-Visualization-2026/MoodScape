import { create } from "zustand";

// stores the current state of the filters
export const useFiltersStore = create((set) => ({
  filters: {
    genre: "",
    yearFrom: undefined,
    yearTo: undefined,
    mainMood: "",
    lyrics: "",
  },

  setFilters: (newFilters) =>
    set(() => ({
      filters: newFilters,
    })),

  setYearRange: (yearFrom, yearTo) =>
    set((state) => ({
      filters: {
        ...state.filters,
        yearFrom,
        yearTo,
      },
    })),

}));