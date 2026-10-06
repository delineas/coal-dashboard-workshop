import { useEffect, useState } from 'react'
import { getJson, NotFoundError } from './api/client'

type State<T> =
  | { status: 'loading' }
  | { status: 'ok'; data: T }
  | { status: 'not-found' }
  | { status: 'error'; message: string }

export function useApi<T>(path: string): State<T> {
  const [state, setState] = useState<{ path: string; value: State<T> }>({ path, value: { status: 'loading' } })

  useEffect(() => {
    let current = true
    getJson<T>(path)
      .then((data) => current && setState({ path, value: { status: 'ok', data } }))
      .catch((e: Error) => {
        if (!current) return
        const value: State<T> = e instanceof NotFoundError ? { status: 'not-found' } : { status: 'error', message: e.message }
        setState({ path, value })
      })
    return () => {
      current = false
    }
  }, [path])

  return state.path === path ? state.value : { status: 'loading' }
}
