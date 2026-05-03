import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import api from '../services/api'

async function fetchDictionaries() {
  const { data } = await api.get('/dictionaries')
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

export default function DictionariesPage() {
  const queryClient = useQueryClient()
  const [confirmDeleteId, setConfirmDeleteId] = useState(null)

  const { data: dictionaries = [], isLoading } = useQuery({
    queryKey: ['dictionaries'],
    queryFn: fetchDictionaries,
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => api.delete(`/dictionaries/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dictionaries'] })
      toast.success('Словник видалено')
      setConfirmDeleteId(null)
    },
    onError: (err) => {
      toast.error(err?.response?.data?.detail ?? 'Не вдалося видалити словник')
    },
  })

  return (
    <div>
      <h1 className="text-xl font-semibold text-gray-800 mb-6">Словники</h1>

      {isLoading ? (
        <p className="text-sm text-gray-500">Завантаження...</p>
      ) : dictionaries.length === 0 ? (
        <div className="text-center py-16 text-gray-400 text-sm">
          Словників ще немає. Вони створюються автоматично при збереженні документів.
        </div>
      ) : (
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase">
                  Предметна область
                </th>
                <th className="px-4 py-2.5 text-center text-xs font-medium text-gray-500 uppercase">
                  Термінів
                </th>
                <th className="px-4 py-2.5" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {dictionaries.map((d) => (
                <tr key={d.id} className="hover:bg-gray-50">
                  <td className="px-4 py-2.5 text-gray-700 font-medium">{d.domain_name}</td>
                  <td className="px-4 py-2.5 text-center text-gray-600">{d.entry_count}</td>
                  <td className="px-4 py-2.5 text-right">
                    {confirmDeleteId === d.id ? (
                      <ConfirmDelete
                        onConfirm={() => deleteMutation.mutate(d.id)}
                        onCancel={() => setConfirmDeleteId(null)}
                      />
                    ) : (
                      <div className="flex items-center justify-end gap-3">
                        <Link
                          to={`/dictionaries/${d.id}`}
                          className="text-blue-500 hover:text-blue-700 text-xs font-medium"
                        >
                          Деталі
                        </Link>
                        <button
                          onClick={() => setConfirmDeleteId(d.id)}
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
