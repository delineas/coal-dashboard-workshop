// Regression test for issue #1: the search "turkey" does not find Türkiye.
// The bug is still open, so test.fails expects a failure today. When someone fixes #1, this test turns red:
// change test.fails to test, and from then on it stops the bug from coming back.
import { expect, test } from 'vitest'
import { matchesCountry } from './search'

test('keeps today\'s behavior: case and spaces have no effect', () => {
  expect(matchesCountry('South Korea', '  kOREA ')).toBe(true)
})

test.fails('"turkey" and "turk" find Türkiye (Refs #1)', () => {
  expect(matchesCountry('Türkiye', 'turkey')).toBe(true)
  expect(matchesCountry('Türkiye', 'turk')).toBe(true)
})
