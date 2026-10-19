// Architecture test: checks a structural rule of the code, not a behavior.
// It protects the API layer: only modules in src/api call fetch. Pages and components use them.
import { expect, test } from 'vitest'

const sources = import.meta.glob<string>(['./pages/**/*.tsx', './components/**/*.tsx'], {
  query: '?raw',
  import: 'default',
  eager: true,
})

test('pages and components never call fetch directly', () => {
  const callers = Object.keys(sources).filter((file) => /\bfetch\(/.test(sources[file]))
  expect(Object.keys(sources).length).toBeGreaterThan(0)
  expect(callers).toEqual([])
})
