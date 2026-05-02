import { QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'

import queryClient from './services/queryClient'
import ErrorBoundary from './components/ErrorBoundary'
import Layout from './components/Layout'
import UploadDocumentPage from './pages/UploadDocumentPage'
import DocumentsListPage from './pages/DocumentsListPage'
import DocumentDetailsPage from './pages/DocumentDetailsPage'
import SpecialistsPage from './pages/SpecialistsPage'
import SpecialistDetailsPage from './pages/SpecialistDetailsPage'
import DictionariesPage from './pages/DictionariesPage'
import DictionaryDetailsPage from './pages/DictionaryDetailsPage'

export default function App() {
  return (
    <ErrorBoundary>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Navigate to="/documents" replace />} />
            <Route path="upload" element={<UploadDocumentPage />} />
            <Route path="documents" element={<DocumentsListPage />} />
            <Route path="documents/:id" element={<DocumentDetailsPage />} />
            <Route path="specialists" element={<SpecialistsPage />} />
            <Route path="specialists/:id" element={<SpecialistDetailsPage />} />
            <Route path="dictionaries" element={<DictionariesPage />} />
            <Route path="dictionaries/:id" element={<DictionaryDetailsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" />
    </QueryClientProvider>
    </ErrorBoundary>
  )
}
