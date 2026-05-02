import { Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import api from '../services/api'

async function fetchDictionary(id) {
  const { data } = await api.get(`/dictionaries/${id}`)
  return data
}

export default function DictionaryDetailsPage() {
  const { id } = useParams()

  const { data: dict, isLoading, isError } = useQuery({
    queryKey: ['dictionary', id],
    queryFn: () => fetchDictionary(id),
  })

  if (isLoading) return <p className="text-sm text-gray-500">Завантаження...</p>
  if (isError) {
    return (
      <div className="text-sm text-red-500">
        Словник не знайдено.{' '}
        <Link to="/dictionaries" className="underline text-gray-500">Назад</Link>
      </div>
    )
  }

  return (
    <div className="max-w-3xl space-y-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-gray-800">
            Словник: {dict.domain_name}
          </h1>
          <p className="text-gray-400 text-sm mt-0.5">{dict.entries.length} термінів</p>
        </div>
        <Link
          to="/dictionaries"
          className="flex-shrink-0 px-4 py-2 border border-gray-300 text-gray-600 text-sm rounded-lg hover:bg-gray-50 transition-colors"
        >
          ← Назад
        </Link>
      </div>

      <div className="border border-gray-200 rounded-lg overflow-hidden bg-white">
        <div className="px-4 py-2.5 bg-gray-50 border-b border-gray-200">
          <h2 className="text-sm font-semibold text-gray-700">Терміни</h2>
        </div>
        {dict.entries.length === 0 ? (
          <p className="px-4 py-3 text-sm text-gray-400">Словник порожній</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                  Термін
                </th>
                <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">
                  Документів
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {dict.entries.map((e) => (
                <tr key={e.term_id} className="hover:bg-gray-50">
                  <td className="px-4 py-2 text-gray-700">{e.term}</td>
                  <td className="px-4 py-2 text-center text-gray-600">{e.document_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
