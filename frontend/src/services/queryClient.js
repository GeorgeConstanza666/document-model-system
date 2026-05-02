import { QueryClient, QueryCache, MutationCache } from '@tanstack/react-query'
import toast from 'react-hot-toast'

function extractMessage(error) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map((e) => e.msg).join('; ')
  return error?.message ?? 'Невідома помилка'
}

const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: (error) => toast.error(`Помилка завантаження: ${extractMessage(error)}`),
  }),
  mutationCache: new MutationCache({
    onError: (error) => toast.error(`Помилка запиту: ${extractMessage(error)}`),
  }),
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
    },
  },
})

export default queryClient
