export function matchesCountry(name: string, query: string): boolean {
  return name.toLowerCase().includes(query.trim().toLowerCase())
}
