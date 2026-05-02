import { NavLink, Outlet } from 'react-router-dom'

const navItems = [
  { to: '/upload', label: 'Завантажити документ' },
  { to: '/documents', label: 'Документи' },
  { to: '/specialists', label: 'Спеціалісти' },
  { to: '/dictionaries', label: 'Словники' },
]

export default function Layout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-6xl mx-auto px-6 flex items-center gap-8 h-14">
          <span className="font-semibold text-gray-800 whitespace-nowrap">
            Документна модель
          </span>
          <nav className="flex gap-1">
            {navItems.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-gray-100 text-gray-900'
                      : 'text-gray-500 hover:text-gray-800 hover:bg-gray-50'
                  }`
                }
              >
                {label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        <Outlet />
      </main>
    </div>
  )
}
