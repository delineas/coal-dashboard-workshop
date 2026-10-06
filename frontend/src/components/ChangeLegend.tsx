import { changeOrder, changes } from '../change'

export default function ChangeLegend() {
  return (
    <div>
      <p className="text-[11px] font-semibold tracking-wider text-zinc-400 uppercase">Plant change 2017 → 2023</p>
      <ul className="mt-2.5 space-y-1.5 text-sm text-zinc-700">
        {changeOrder.map((key) => (
          <li key={key} className="flex items-center gap-2">
            <span
              className="h-2.5 w-2.5 rounded-full border"
              style={{ background: changes[key].fill, borderColor: changes[key].stroke }}
            />
            {changes[key].label}
          </li>
        ))}
      </ul>
    </div>
  )
}
