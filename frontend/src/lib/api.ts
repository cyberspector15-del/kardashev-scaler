const api = import.meta.env.VITE_API_BASE_URL;

if (!api) {
  console.warn("VITE_API_BASE_URL is not set in the environment. Using relative paths.");
}

export async function post<T>(path: string, body: object) {
  const url = api ? `${api}${path}` : path;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail ?? 'The request could not be completed.');
  return data as T;
}
