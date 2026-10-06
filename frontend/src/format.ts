const mwFormat = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 })

export function formatMw(value: number): string {
  return mwFormat.format(value)
}
