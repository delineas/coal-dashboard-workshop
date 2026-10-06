import { useEffect, useState } from 'react'

interface Hello {
  message: string
  sqlite: string
}

export default function App() {
  const [hello, setHello] = useState<Hello | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/hello')
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`API error ${r.status}`))))
      .then(setHello)
      .catch((e: Error) => setError(e.message))
  }, [])

  return (
    <main className="mx-auto max-w-2xl p-6 text-gray-900">
      <p className="text-sm text-gray-500">Basecamp Tool</p>
      <h1 className="mt-1 text-4xl font-semibold">{error ?? hello?.message ?? 'Loading…'}</h1>
      {hello && <p className="mt-2 text-sm text-gray-500">From the API · SQLite {hello.sqlite}</p>}
    </main>
  )
}
