import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import api from '../services/api'

async function fetchSpecialists() {
  const { data } = await api.get('/specialists')
  return data
}

function ConfirmDelete({ onConfirm, onCancel }) {
  return (
    <span className="flex items-center gap-2">
      <button
        onClick={onConfirm}
        className="text-red-600 text-xs font-medium hover:underline"
      >
        Підтвердити
      </button>
      <button
        onClick={onCancel}
        className="text-gray-400 text-xs hover:text-gray-600"
      >
        Скасувати
      </button>
    </span>
  )
}

export default function SpecialistsPage() {
  const queryClient = useQueryClient()
  const [confirmDeleteId, setConfirmDeleteId] = useState(null)

  const { data: specialists = [], isLoading } = useQuery({
    queryKey: ['specialists'],
    queryFn: fetchSpecialists,
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => api.delete(`/specialists/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['specialists'] })
      toast.success('Спеціаліста видалено')
      setConfirmDeleteId(null)
    },
    onError: (err) => {
      toast.error(err?.response?.data?.detail ?? 'Не вдалося видалити спеціаліста')
    },
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
                    {confirmDeleteId === s.id ? (
                      <ConfirmDelete
                        onConfirm={() => deleteMutation.mutate(s.id)}
                        onCancel={() => setConfirmDeleteId(null)}
                      />
                    ) : (
                      <div className="flex items-center justify-end gap-3">
                        <Link
                          to={`/specialists/${s.id}`}
                          className="text-blue-500 hover:text-blue-700 text-xs font-medium"
                        >
                          Деталі
                        </Link>
                        <button
                          onClick={() => setConfirmDeleteId(s.id)}
                          className="text-red-400 hover:text-red-600 text-xs"
                        >
                          Видалити
                        </button>
                      </div>
                    )}
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
