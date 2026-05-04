import { useNavigation } from '../hooks/useNavigation'

export function Navigation() {
  const { getNavOptions } = useNavigation()
  const options = getNavOptions()

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-gray-900 text-white p-4">
      <div className="max-w-lg mx-auto flex justify-around">
        {options.map((opt, idx) => (
          <button
            key={idx}
            onClick={opt.action}
            className="flex flex-col items-center gap-1 px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
          >
            <span className="text-2xl font-bold">{idx + 1}</span>
            <span className="text-sm">{opt.label}</span>
          </button>
        ))}
      </div>
    </nav>
  )
}
