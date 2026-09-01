import { useCallback, useEffect, useState } from 'react'
import { getErrorMessage } from '../services/api'

export function useApi(loader, dependencies = [], options = {}) {
  const { immediate = true } = options
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(immediate)
  const [error, setError] = useState('')

  const run = useCallback(async (...args) => {
    setLoading(true)
    setError('')
    try {
      const result = await loader(...args)
      setData(result)
      return result
    } catch (requestError) {
      const message = getErrorMessage(requestError)
      setError(message)
      throw requestError
    } finally {
      setLoading(false)
    }
  }, dependencies)

  useEffect(() => {
    if (immediate) run().catch(() => {})
  }, [run, immediate])

  return { data, loading, error, run, setData }
}
