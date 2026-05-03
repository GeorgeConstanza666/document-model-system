import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import api from '../services/api'

async function fetchDocument(id) {
  const { data } = await api.get(`/documents/${id}`)
  return data
}

function Section({ title, children }) {
  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden bg-white">
      <div className="px-4 py-2.5 bg-gray-50 border-b border-gray-200">
        <h2 className="text-sm font-semibold text-gray-700">{title}</h2>
      </div>
      {children}
    </div>
  )
}

function Collapsible({ title, children }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="border border-gray-200 rounded-lg bg-white">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-4 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
      >
        {title}
        <span className="text-gray-400 text-xs">{open ? '▲' : '▼'}</span>
      </button>
      {open && (
        <div className="px-4 pb-4 border-t border-gray-100">
          {children}
        </div>
      )}
    </div>
  )
}

export default function DocumentDetailsPage() {
  const { id } = useParams()

  const { data: doc, isLoading, isError } = useQuery({
    queryKey: ['document', id],
    queryFn: () => fetchDocument(id),
  })

  if (isLoading) {
    return <p className="text-sm text-gray-500">Завантаження...</p>
  }
  if (isError) {
    return (
      <div className="text-sm text-red-500">
        Документ не знайдено.{' '}
        <Link to="/documents" className="underline text-gray-500">
          Повернутися до списку
        </Link>
      </div>
    )
  }

  const sortedTerms = [...doc.terms].sort((a, b) => b.rel_freq_term - a.rel_freq_term)

  return (
    <div className="max-w-3xl space-y-5">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-gray-800">
            {doc.file_name ?? `Документ #${doc.id}`}
          </h1>
          <p className="text-gray-400 text-sm mt-0.5">
            {doc.date}
            {doc.source_language && (
              <span className="ml-2 px-1.5 py-0.5 bg-gray-100 text-gray-500 rounded text-xs uppercase">
                {doc.source_language}
              </span>
            )}
          </p>
        </div>
        <Link
          to="/documents"
          className="flex-shrink-0 px-4 py-2 border border-gray-300 text-gray-600 text-sm rounded-lg hover:bg-gray-50 transition-colors"
        >
          ← Назад до списку
        </Link>
      </div>

      {/* Domain */}
      <Section title="Предметна область">
        <p className="px-4 py-2.5 text-sm text-gray-700">{doc.subject_area}</p>
      </Section>

      {/* Authors */}
      <Section title="Автори">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                Ім'я
              </th>
              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">
                Внесок, %
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {doc.authors.map((a) => (
              <tr key={a.author_id} className="hover:bg-gray-50">
                <td className="px-4 py-2 text-gray-700">{a.full_name}</td>
                <td className="px-4 py-2 text-center text-gray-600">
                  {a.contribution_percent.toFixed(1)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Section>

      {/* Terms */}
      <Section title={`Терміни (${doc.terms.length})`}>
        {doc.terms.length === 0 ? (
          <p className="px-4 py-2.5 text-sm text-gray-400">Терміни відсутні</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                  Термін
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                  Визначення
                </th>
                <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">
                  К-сть
                </th>
                <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">
                  Відн. частота, %
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {sortedTerms.map((t) => (
                <tr key={t.term_id} className="hover:bg-gray-50">
                  <td className="px-4 py-2 text-gray-700">{t.term}</td>
                  <td className="px-4 py-2 text-gray-500 text-xs max-w-[220px]">
                    {t.definition
                      ? <span title={t.definition} className="line-clamp-2">{t.definition}</span>
                      : <span className="text-gray-300 italic">—</span>}
                  </td>
                  <td className="px-4 py-2 text-center text-gray-600">{t.q_term}</td>
                  <td className="px-4 py-2 text-center text-gray-600">
                    {t.rel_freq_term.toFixed(4)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Section>

      {/* Technologies */}
      <Section title={`Технології (${doc.technologies.length})`}>
        {doc.technologies.length === 0 ? (
          <p className="px-4 py-2.5 text-sm text-gray-400">Технології відсутні</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                  Назва
                </th>
                <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">
                  Ступінь використання, %
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {doc.technologies.map((t) => (
                <tr key={t.technology_id} className="hover:bg-gray-50">
                  <td className="px-4 py-2 text-gray-700">{t.technology_name}</td>
                  <td className="px-4 py-2 text-center text-gray-600">
                    {t.degree_of_use.toFixed(1)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Section>

      {/* Full text collapsibles */}
      <Collapsible title="Оригінальний текст">
        <pre className="mt-3 text-xs text-gray-600 whitespace-pre-wrap max-h-64 overflow-y-auto leading-relaxed">
          {doc.original_text || '—'}
        </pre>
      </Collapsible>

      <Collapsible title="Переклад на англійську">
        <pre className="mt-3 text-xs text-gray-600 whitespace-pre-wrap max-h-64 overflow-y-auto leading-relaxed">
          {doc.translated_text || '—'}
        </pre>
      </Collapsible>
    </div>
  )
}
