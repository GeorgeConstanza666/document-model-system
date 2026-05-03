import { Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import api from '../services/api'

async function fetchSpecialist(id) {
  const { data } = await api.get(`/specialists/${id}`)
  return data
}

export default function SpecialistDetailsPage() {
  const { id } = useParams()

  const { data: spec, isLoading, isError } = useQuery({
    queryKey: ['specialist', id],
    queryFn: () => fetchSpecialist(id),
  })

  if (isLoading) return <p className="text-sm text-gray-500">Завантаження...</p>
  if (isError) {
    return (
      <div className="text-sm text-red-500">
        Спеціаліста не знайдено.{' '}
        <Link to="/specialists" className="underline text-gray-500">Назад</Link>
      </div>
    )
  }

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-gray-800">{spec.full_name}</h1>
          {spec.email && <p className="text-gray-400 text-sm mt-0.5">{spec.email}</p>}
        </div>
        <Link
          to="/specialists"
          className="flex-shrink-0 px-4 py-2 border border-gray-300 text-gray-600 text-sm rounded-lg hover:bg-gray-50 transition-colors"
        >
          ← Назад
        </Link>
      </div>

      {/* Documents */}
      <div className="border border-gray-200 rounded-lg overflow-hidden bg-white">
        <div className="px-4 py-2.5 bg-gray-50 border-b border-gray-200">
          <h2 className="text-sm font-semibold text-gray-700">
            Документи ({spec.documents.length})
          </h2>
        </div>
        {spec.documents.length === 0 ? (
          <p className="px-4 py-3 text-sm text-gray-400">Немає документів</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Файл</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Домен</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Дата</th>
                <th className="px-4 py-2" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {spec.documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-gray-50">
                  <td className="px-4 py-2 text-gray-700">{doc.file_name ?? `#${doc.id}`}</td>
                  <td className="px-4 py-2 text-gray-500">{doc.subject_area}</td>
                  <td className="px-4 py-2 text-gray-500 whitespace-nowrap">{doc.date}</td>
                  <td className="px-4 py-2 text-right">
                    <Link
                      to={`/documents/${doc.id}`}
                      className="text-blue-500 hover:text-blue-700 text-xs font-medium"
                    >
                      Деталі
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Unique terms */}
      <div className="border border-gray-200 rounded-lg overflow-hidden bg-white">
        <div className="px-4 py-2.5 bg-gray-50 border-b border-gray-200">
          <h2 className="text-sm font-semibold text-gray-700">
            Унікальні терміни ({spec.unique_terms.length})
          </h2>
        </div>
        {spec.unique_terms.length === 0 ? (
          <p className="px-4 py-3 text-sm text-gray-400">Терміни відсутні</p>
        ) : (
          <div className="px-4 py-3 flex flex-wrap gap-2">
            {spec.unique_terms.map((term) => (
              <span
                key={term}
                className="px-2.5 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
              >
                {term}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Unique technologies */}
      <div className="border border-gray-200 rounded-lg overflow-hidden bg-white">
        <div className="px-4 py-2.5 bg-gray-50 border-b border-gray-200">
          <h2 className="text-sm font-semibold text-gray-700">
            Технології ({spec.unique_technologies.length})
          </h2>
        </div>
        {spec.unique_technologies.length === 0 ? (
          <p className="px-4 py-3 text-sm text-gray-400">Технології відсутні</p>
        ) : (
          <div className="px-4 py-3 flex flex-wrap gap-2">
            {spec.unique_technologies.map((tech) => (
              <span
                key={tech}
                className="px-2.5 py-1 bg-blue-50 text-blue-700 text-xs rounded-full"
              >
                {tech}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
