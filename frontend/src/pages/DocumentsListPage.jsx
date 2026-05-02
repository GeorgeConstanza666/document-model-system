import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import api from '../services/api'

async function fetchDocuments() {
  const { data } = await api.get('/documents?page=1&page_size=1000')
  return data.items
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

export default function DocumentsListPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [domainFilter, setDomainFilter] = useState('')
  const [sortAsc, setSortAsc] = useState(false)
  const [confirmDeleteId, setConfirmDeleteId] = useState(null)

  const { data: docs = [], isLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: fetchDocuments,
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => api.delete(`/documents/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      toast.success('Документ видалено')
      setConfirmDeleteId(null)
    },
    onError: (err) => {
      toast.error(err?.response?.data?.detail ?? 'Не вдалося видалити документ')
    },
  })

  const domains = useMemo(() => {
    const set = new Set(docs.map((d) => d.subject_area))
    return [...set].sort()
  }, [docs])

  const filtered = useMemo(() => {
    let result = docs
    if (search.trim()) {
      const q = search.trim().toLowerCase()
      result = result.filter((d) => (d.file_name ?? '').toLowerCase().includes(q))
    }
    if (domainFilter) {
      result = result.filter((d) => d.subject_area === domainFilter)
    }
    return [...result].sort((a, b) => {
      const cmp = a.date.localeCompare(b.date)
      return sortAsc ? cmp : -cmp
    })
  }, [docs, search, domainFilter, sortAsc])

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-semibold text-gray-800">Документи</h1>
        <Link
          to="/upload"
          className="px-4 py-2 bg-gray-800 text-white text-sm font-medium rounded-lg hover:bg-gray-700 transition-colors"
        >
          + Завантажити
        </Link>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-4 flex-wrap">
        <input
          type="text"
          placeholder="Пошук за назвою файлу..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-gray-400 w-64"
        />
        <select
          value={domainFilter}
          onChange={(e) => setDomainFilter(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm text-gray-700 focus:outline-none focus:border-gray-400 bg-white"
        >
          <option value="">Всі домени</option>
          {domains.map((d) => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
        <button
          onClick={() => setSortAsc((s) => !s)}
          className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 transition-colors"
        >
          Дата {sortAsc ? '↑ старі' : '↓ нові'}
        </button>
      </div>

      {isLoading ? (
        <p className="text-sm text-gray-500">Завантаження...</p>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16 text-gray-400 text-sm">
          {docs.length === 0
            ? 'Ще немає жодного документа. Завантажте перший!'
            : 'Нічого не знайдено за вказаними фільтрами.'}
        </div>
      ) : (
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase">Дата</th>
                <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase">Файл</th>
                <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase">Домен</th>
                <th className="px-4 py-2.5 text-center text-xs font-medium text-gray-500 uppercase">Авторів</th>
                <th className="px-4 py-2.5 text-center text-xs font-medium text-gray-500 uppercase">Термінів</th>
                <th className="px-4 py-2.5" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.map((doc) => (
                <tr key={doc.id} className="hover:bg-gray-50">
                  <td className="px-4 py-2.5 text-gray-400 font-mono text-xs">{doc.id}</td>
                  <td className="px-4 py-2.5 text-gray-600 whitespace-nowrap">{doc.date}</td>
                  <td className="px-4 py-2.5 text-gray-700 max-w-[180px] truncate" title={doc.file_name ?? ''}>
                    {doc.file_name ?? '—'}
                  </td>
                  <td className="px-4 py-2.5 text-gray-600">{doc.subject_area}</td>
                  <td className="px-4 py-2.5 text-center text-gray-600">{doc.authors.length}</td>
                  <td className="px-4 py-2.5 text-center text-gray-600">{doc.term_count}</td>
                  <td className="px-4 py-2.5 text-right">
                    {confirmDeleteId === doc.id ? (
                      <ConfirmDelete
                        onConfirm={() => deleteMutation.mutate(doc.id)}
                        onCancel={() => setConfirmDeleteId(null)}
                      />
                    ) : (
                      <div className="flex items-center justify-end gap-3">
                        <Link
                          to={`/documents/${doc.id}`}
                          className="text-blue-500 hover:text-blue-700 text-xs font-medium"
                        >
                          Деталі
                        </Link>
                        <button
                          onClick={() => setConfirmDeleteId(doc.id)}
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
