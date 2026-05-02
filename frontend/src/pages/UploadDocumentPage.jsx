import { useRef, useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import api from '../services/api'

const ACCEPTED = ['docx', 'pdf', 'txt']

async function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post('/documents/upload', formData, {
    headers: { 'Content-Type': undefined },
  })
  return data
}

// ─── Shared UI ────────────────────────────────────────────────────────────────

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

// ─── Step indicator ───────────────────────────────────────────────────────────

const STEP_LABELS = ['Вибір файлу', 'Перегляд', 'Збереження']

function StepIndicator({ current }) {
  return (
    <div className="flex items-center gap-2 mb-8">
      {STEP_LABELS.map((label, i) => {
        const num = i + 1
        const active = num === current
        const done = num < current
        return (
          <div key={num} className="flex items-center gap-2">
            <div
              className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold ${
                done
                  ? 'bg-green-500 text-white'
                  : active
                  ? 'bg-gray-800 text-white'
                  : 'bg-gray-200 text-gray-500'
              }`}
            >
              {done ? '✓' : num}
            </div>
            <span className={`text-sm ${active ? 'text-gray-800 font-medium' : 'text-gray-400'}`}>
              {label}
            </span>
            {i < STEP_LABELS.length - 1 && <div className="w-8 h-px bg-gray-200 mx-1" />}
          </div>
        )
      })}
    </div>
  )
}

// ─── Step 1 ───────────────────────────────────────────────────────────────────

function DropZone({ onFile }) {
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef(null)

  const validate = (f) => {
    if (!f) return
    const ext = f.name.split('.').pop().toLowerCase()
    if (!ACCEPTED.includes(ext)) {
      toast.error('Підтримуються лише файли .docx, .pdf, .txt')
      return
    }
    onFile(f)
  }

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => { e.preventDefault(); setIsDragging(false); validate(e.dataTransfer.files[0]) }}
      onClick={() => inputRef.current?.click()}
      className={`border-2 border-dashed rounded-xl p-16 text-center cursor-pointer transition-colors select-none ${
        isDragging
          ? 'border-blue-400 bg-blue-50'
          : 'border-gray-300 bg-white hover:border-gray-400 hover:bg-gray-50'
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".docx,.pdf,.txt"
        className="hidden"
        onChange={(e) => validate(e.target.files[0])}
      />
      <div className="text-4xl mb-3">📄</div>
      <p className="text-gray-600 font-medium">
        Перетягніть файл сюди або{' '}
        <span className="text-blue-600 underline">оберіть файл</span>
      </p>
      <p className="text-gray-400 text-sm mt-1">.docx, .pdf, .txt</p>
    </div>
  )
}

function StepOne({ onSuccess }) {
  const [file, setFile] = useState(null)

  const mutation = useMutation({
    mutationFn: uploadFile,
    onSuccess,
    onError: (err) => {
      const msg = err?.response?.data?.detail ?? 'Не вдалося обробити документ'
      toast.error(msg)
    },
  })

  return (
    <div className="max-w-2xl">
      <DropZone onFile={setFile} />

      {file && (
        <div className="mt-4 p-4 bg-white border border-gray-200 rounded-lg flex items-center justify-between">
          <div className="flex items-center gap-3 min-w-0">
            <span className="text-gray-400 text-lg">📎</span>
            <span className="text-gray-700 text-sm font-medium truncate">{file.name}</span>
          </div>
          <button
            onClick={() => setFile(null)}
            className="text-gray-400 hover:text-gray-600 ml-4 flex-shrink-0 text-lg leading-none"
          >
            ×
          </button>
        </div>
      )}

      {mutation.isPending && (
        <div className="mt-6 flex items-center gap-3 text-gray-600 text-sm">
          <svg className="animate-spin h-5 w-5 text-blue-500 flex-shrink-0" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
          </svg>
          Обробка документа... це може зайняти до 60 секунд
        </div>
      )}

      <button
        onClick={() => mutation.mutate(file)}
        disabled={!file || mutation.isPending}
        className="mt-6 px-5 py-2.5 bg-gray-800 text-white text-sm font-medium rounded-lg
                   hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
      >
        Обробити документ
      </button>
    </div>
  )
}

// ─── Step 2 ───────────────────────────────────────────────────────────────────

function TermsTable({ terms, onRemove, onChangeQTerm }) {
  const [editingIdx, setEditingIdx] = useState(null)
  const [editVal, setEditVal] = useState('')

  const start = (i, current) => { setEditingIdx(i); setEditVal(String(current)) }

  const commit = (i) => {
    const v = parseInt(editVal, 10)
    if (!isNaN(v) && v >= 0) onChangeQTerm(i, v)
    setEditingIdx(null)
  }

  if (terms.length === 0) {
    return <p className="text-sm text-gray-400 py-2">Терміни відсутні</p>
  }

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Термін</th>
            <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">
              Кількість входжень
            </th>
            <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">
              Відносна частота, %
            </th>
            <th className="px-4 py-2" />
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {terms.map((t, i) => (
            <tr key={i} className="hover:bg-gray-50">
              <td className="px-4 py-2 text-gray-700">{t.term}</td>
              <td className="px-4 py-2 text-center">
                {editingIdx === i ? (
                  <input
                    autoFocus
                    type="number"
                    min="0"
                    value={editVal}
                    onChange={(e) => setEditVal(e.target.value)}
                    onBlur={() => commit(i)}
                    onKeyDown={(e) => { if (e.key === 'Enter') commit(i) }}
                    className="w-16 text-center border border-blue-400 rounded px-1 py-0.5 text-sm focus:outline-none"
                  />
                ) : (
                  <span
                    onClick={() => start(i, t.q_term)}
                    className="cursor-pointer hover:underline text-gray-700"
                    title="Клікніть для редагування"
                  >
                    {t.q_term}
                  </span>
                )}
              </td>
              <td className="px-4 py-2 text-center text-gray-500">
                {t.rel_freq_term.toFixed(4)}
              </td>
              <td className="px-4 py-2 text-right">
                <button
                  onClick={() => onRemove(i)}
                  className="text-red-400 hover:text-red-600 text-xs"
                >
                  Видалити
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function TechnologiesTable({ technologies, onRemove, onAdd }) {
  const [name, setName] = useState('')
  const [degree, setDegree] = useState('')

  const add = () => {
    const trimmed = name.trim()
    const deg = parseFloat(degree)
    if (!trimmed) { toast.error('Введіть назву технології'); return }
    if (isNaN(deg) || deg < 0 || deg > 100) { toast.error('Ступінь використання: 0–100'); return }
    if (technologies.some((t) => t.name.toLowerCase() === trimmed.toLowerCase())) {
      toast.error('Технологія вже є в списку'); return
    }
    onAdd({ name: trimmed, degree_of_use: deg })
    setName('')
    setDegree('')
  }

  return (
    <div className="space-y-3">
      {technologies.length > 0 && (
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Назва</th>
                <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">
                  Ступінь використання, %
                </th>
                <th className="px-4 py-2" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {technologies.map((t, i) => (
                <tr key={i} className="hover:bg-gray-50">
                  <td className="px-4 py-2 text-gray-700">{t.name}</td>
                  <td className="px-4 py-2 text-center text-gray-700">{t.degree_of_use.toFixed(1)}</td>
                  <td className="px-4 py-2 text-right">
                    <button
                      onClick={() => onRemove(i)}
                      className="text-red-400 hover:text-red-600 text-xs"
                    >
                      Видалити
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Add row */}
      <div className="flex gap-2 items-end">
        <div>
          <label className="block text-xs text-gray-500 mb-1">Назва технології</label>
          <input
            type="text"
            placeholder="Python"
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') add() }}
            className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-gray-400 w-48"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">Ступінь, %</label>
          <input
            type="number"
            placeholder="10"
            min="0"
            max="100"
            value={degree}
            onChange={(e) => setDegree(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') add() }}
            className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-gray-400 w-24"
          />
        </div>
        <button
          onClick={add}
          className="px-3 py-1.5 bg-white border border-gray-300 text-gray-700 text-sm rounded-lg
                     hover:bg-gray-50 transition-colors"
        >
          + Додати
        </button>
      </div>
    </div>
  )
}

function StepTwo({ processed, onBack, onNext }) {
  const [terms, setTerms] = useState(processed?.extracted_terms ?? [])
  const [technologies, setTechnologies] = useState(processed?.extracted_technologies ?? [])

  const removeTermAt = (i) => setTerms((ts) => ts.filter((_, idx) => idx !== i))
  const changeQTerm = (i, val) =>
    setTerms((ts) => ts.map((t, idx) => (idx === i ? { ...t, q_term: val } : t)))

  const removeTechAt = (i) => setTechnologies((ts) => ts.filter((_, idx) => idx !== i))
  const addTech = (tech) => setTechnologies((ts) => [...ts, tech])

  return (
    <div className="max-w-3xl space-y-5">
      <Collapsible title="Оригінальний текст">
        <pre className="mt-3 text-xs text-gray-600 whitespace-pre-wrap max-h-48 overflow-y-auto leading-relaxed">
          {processed?.original_text || '—'}
        </pre>
      </Collapsible>

      <Collapsible title="Переклад на англійську">
        <pre className="mt-3 text-xs text-gray-600 whitespace-pre-wrap max-h-48 overflow-y-auto leading-relaxed">
          {processed?.translated_text || '—'}
        </pre>
      </Collapsible>

      <div>
        <h2 className="text-sm font-semibold text-gray-700 mb-2">
          Витягнуті терміни{' '}
          <span className="font-normal text-gray-400">({terms.length})</span>
        </h2>
        <TermsTable
          terms={terms}
          onRemove={removeTermAt}
          onChangeQTerm={changeQTerm}
        />
      </div>

      <div>
        <h2 className="text-sm font-semibold text-gray-700 mb-2">
          Витягнуті технології{' '}
          <span className="font-normal text-gray-400">({technologies.length})</span>
        </h2>
        <TechnologiesTable
          technologies={technologies}
          onRemove={removeTechAt}
          onAdd={addTech}
        />
      </div>

      <div className="flex justify-between pt-2">
        <button
          onClick={onBack}
          className="px-5 py-2.5 border border-gray-300 text-gray-600 text-sm font-medium rounded-lg
                     hover:bg-gray-50 transition-colors"
        >
          ← Назад
        </button>
        <button
          onClick={() => onNext({ terms, technologies })}
          className="px-5 py-2.5 bg-gray-800 text-white text-sm font-medium rounded-lg
                     hover:bg-gray-700 transition-colors"
        >
          Далі: Автори →
        </button>
      </div>
    </div>
  )
}

// ─── Step 3 placeholder ───────────────────────────────────────────────────────

function StepThree() {
  return (
    <div className="max-w-2xl">
      <div className="p-6 bg-white border border-gray-200 rounded-xl text-center text-gray-500 text-sm">
        Крок 3 — введення авторів та збереження — буде реалізовано далі.
      </div>
    </div>
  )
}

// ─── Page root ────────────────────────────────────────────────────────────────

export default function UploadDocumentPage() {
  const [step, setStep] = useState(1)
  const [draftId, setDraftId] = useState(null)
  const [processed, setProcessed] = useState(null)
  const [editedData, setEditedData] = useState(null)

  const handleUploadSuccess = (data) => {
    setDraftId(data.draft_id)
    setProcessed(data.processed)
    setStep(2)
  }

  const handleStepTwoNext = (data) => {
    setEditedData(data)
    setStep(3)
  }

  return (
    <div>
      <h1 className="text-xl font-semibold text-gray-800 mb-6">Завантажити документ</h1>
      <StepIndicator current={step} />

      {step === 1 && <StepOne onSuccess={handleUploadSuccess} />}
      {step === 2 && (
        <StepTwo
          processed={processed}
          onBack={() => setStep(1)}
          onNext={handleStepTwoNext}
        />
      )}
      {step === 3 && (
        <StepThree draftId={draftId} processed={processed} editedData={editedData} />
      )}
    </div>
  )
}
