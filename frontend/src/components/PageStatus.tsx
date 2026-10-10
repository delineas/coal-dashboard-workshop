import { Link } from 'react-router'

export function Loading() {
  return <p className="text-zinc-500">Loading…</p>
}

export function LoadError({ message }: { message: string }) {
  return <p className="text-red-700">{message}</p>
}

export function NotFound() {
  return (
    <div className="py-16 text-center">
      <h1 className="text-xl font-semibold">Not found</h1>
      <p className="mt-2 text-sm text-zinc-500">The page you asked for does not exist.</p>
      <Link to="/" className="mt-4 inline-block text-sm font-medium text-brand-600 hover:underline">
        Go to the overview
      </Link>
    </div>
  )
}
