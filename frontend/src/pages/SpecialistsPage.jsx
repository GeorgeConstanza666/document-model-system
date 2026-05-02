import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import api from '../services/api'

async function fetchSpecialists() {
  const { data } = await api.get('/specialists')
  return data
}

export default function SpecialistsPage() {
  const { data: specialists = [], isLoading } = useQuery({
    queryKey: ['specialists'],
    queryFn: fetchSpecialists,
  })

  return (
    <div>
      <h1 className="text-xl font-semibold text-gray-800 mb-6">Спеціалісти</h1>

      {isLoading ? (
        <p className="text-sm text-gray-500">Завантаження...</p>
      ) : specialists.length === 0 ? (
        <div className="text-center py-16 text-gray-400 text-sm">
          Спеціалістів ще немає. Вони з'являться після збереження першого документа.
        </div>
      ) : (
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase">
                  Ім'я
                </th>
                <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase">
                  Email
                </th>
                <th className="px-4 py-2.5 text-center text-xs font-medium text-gray-500 uppercase">
                  Документів
                </th>
                <th className="px-4 py-2.5 text-center text-xs font-medium text-gray-500 uppercase">
                  Унікальних термінів
                </th>
                <th className="px-4 py-2.5" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {specialists.map((s) => (
                <tr key={s.id} className="hover:bg-gray-50">
                  <td className="px-4 py-2.5 text-gray-700 font-medium">{s.full_name}</td>
                  <td className="px-4 py-2.5 text-gray-500">{s.email ?? '—'}</td>
                  <td className="px-4 py-2.5 text-center text-gray-600">{s.document_count}</td>
                  <td className="px-4 py-2.5 text-center text-gray-600">{s.unique_term_count}</td>
                  <td className="px-4 py-2.5 text-right">
                    <Link
                      to={`/specialists/${s.id}`}
                      className="text-blue-500 hover:text-blue-700 text-xs font-medium"
                    >
                      Деталі
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
