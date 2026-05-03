import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import api from '../services/api'

async function fetchDictionary(id) {
  const { data } = await api.get(`/dictionaries/${id}`)
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

function DefinitionCell({ entry }) {
  const queryClient = useQueryClient()
  const [editing, setEditing] = useState(false)
  const [value, setValue] = useState(entry.definition ?? '')

  const saveMutation = useMutation({
    mutationFn: (text) =>
      api.patch(`/terms/${entry.term_id}`, { definition: text || null }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dictionary'] })
      toast.success('Визначення збережено')
      setEditing(false)
    },
    onError: () => toast.error('Не вдалося зберегти визначення'),
  })

  if (editing) {
    return (
      <td className="px-4 py-2" colSpan={3}>
        <div className="flex items-start gap-2">
          <textarea
            autoFocus
            value={value}
            onChange={(e) => setValue(e.target.value)}
            rows={2}
            className="flex-1 border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:border-gray-400 resize-none"
            placeholder="Введіть визначення терміна..."
          />
          <div className="flex flex-col gap-1">
            <button
              onClick={() => saveMutation.mutate(value)}
              disabled={saveMutation.isPending}
              className="px-3 py-1 bg-gray-800 text-white text-xs rounded hover:bg-gray-700 disabled:opacity-50"
            >
              Зберегти
            </button>
            <button
              onClick={() => { setValue(entry.definition ?? ''); setEditing(false) }}
              className="px-3 py-1 border border-gray-300 text-gray-500 text-xs rounded hover:bg-gray-50"
            >
              Скасувати
            </button>
          </div>
        </div>
      </td>
    )
  }

  return (
    <td className="px-4 py-2 text-gray-600 text-sm">
      <div className="flex items-center gap-2 group">
        <span className={entry.definition ? '' : 'text-gray-300 italic'}>
          {entry.definition || 'не задано'}
        </span>
        <button
          onClick={() => { setValue(entry.definition ?? ''); setEditing(true) }}
          className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-gray-600 text-xs transition-opacity"
          title="Редагувати визначення"
        >
          ✎
        </button>
      </div>
    </td>
  )
}

export default function DictionaryDetailsPage() {
  const { id } = useParams()
  const queryClient = useQueryClient()
  const [confirmDeleteTermId, setConfirmDeleteTermId] = useState(null)

  const { data: dict, isLoading, isError } = useQuery({
    queryKey: ['dictionary', id],
    queryFn: () => fetchDictionary(id),
  })

  const deleteTermMutation = useMutation({
    mutationFn: (termId) => api.delete(`/dictionaries/${id}/terms/${termId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dictionary', id] })
      queryClient.invalidateQueries({ queryKey: ['dictionaries'] })
      toast.success('Термін видалено зі словника')
      setConfirmDeleteTermId(null)
    },
    onError: (err) =>
      toast.error(err?.response?.data?.detail ?? 'Не вдалося видалити термін'),
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
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase w-1/4">
                  Термін
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                  Визначення
                </th>
                <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase w-24">
                  Документів
                </th>
                <th className="px-4 py-2 w-28" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {dict.entries.map((e) => (
                <tr key={e.term_id} className="hover:bg-gray-50 align-top">
                  <td className="px-4 py-2 text-gray-700 font-medium">{e.term}</td>
                  <DefinitionCell entry={e} />
                  {confirmDeleteTermId !== e.term_id && (
                    <td className="px-4 py-2 text-center text-gray-600">{e.document_count}</td>
                  )}
                  <td className="px-4 py-2 text-right">
                    {confirmDeleteTermId === e.term_id ? (
                      <ConfirmDelete
                        onConfirm={() => deleteTermMutation.mutate(e.term_id)}
                        onCancel={() => setConfirmDeleteTermId(null)}
                      />
                    ) : (
                      <button
                        onClick={() => setConfirmDeleteTermId(e.term_id)}
                        className="text-red-400 hover:text-red-600 text-xs"
                      >
                        Видалити
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
