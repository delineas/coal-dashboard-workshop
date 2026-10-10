export class NotFoundError extends Error {}

export async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(path)
  if (response.status === 404) throw new NotFoundError(path)
  if (!response.ok) throw new Error(`API error ${response.status}`)
  return response.json()
}
