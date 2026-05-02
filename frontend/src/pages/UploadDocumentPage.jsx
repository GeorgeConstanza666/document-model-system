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
            title="Видалити"
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

function StepTwo() {
  return (
    <div className="max-w-2xl">
      <div className="p-6 bg-white border border-gray-200 rounded-xl text-center text-gray-500 text-sm">
        Крок 2 — перегляд і підтвердження даних — буде реалізовано далі.
      </div>
    </div>
  )
}

export default function UploadDocumentPage() {
  const [step, setStep] = useState(1)
  const [draftId, setDraftId] = useState(null)
  const [processed, setProcessed] = useState(null)

  const handleUploadSuccess = (data) => {
    setDraftId(data.draft_id)
    setProcessed(data.processed)
    setStep(2)
  }

  const steps = ['Вибір файлу', 'Підтвердження', 'Збереження']

  return (
    <div>
      <h1 className="text-xl font-semibold text-gray-800 mb-6">
        Завантажити документ
      </h1>

      {/* Step indicator */}
      <div className="flex items-center gap-2 mb-8">
        {steps.map((label, i) => {
          const num = i + 1
          const active = num === step
          const done = num < step
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
              <span
                className={`text-sm ${active ? 'text-gray-800 font-medium' : 'text-gray-400'}`}
              >
                {label}
              </span>
              {i < steps.length - 1 && (
                <div className="w-8 h-px bg-gray-200 mx-1" />
              )}
            </div>
          )
        })}
      </div>

      {step === 1 && <StepOne onSuccess={handleUploadSuccess} />}
      {step === 2 && <StepTwo draftId={draftId} processed={processed} />}
    </div>
  )
}
