import axios from "axios";

// create an axios instance to avoid repeating backend base url in requests
export const api = axios.create({
  baseURL: "http://localhost:8000",
});

export const apiGo = axios.create({
  baseURL: "http://localhost:8004",
});
