const defaultApiBaseUrl = "https://finalyear-project-e0u2.onrender.com";

export const apiBaseUrl =
  (process.env.NEXT_PUBLIC_API_URL || defaultApiBaseUrl).replace(/\/+$/, "");

export function apiUrl(path: string) {
  return `${apiBaseUrl}${path.startsWith("/") ? path : `/${path}`}`;
}
