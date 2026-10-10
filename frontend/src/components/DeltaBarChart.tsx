import { Bar, BarChart, Cell, LabelList, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { Country } from '../api/countries'
import { formatSignedGw } from '../format'
import Card from './Card'

const TOP_N = 20
const INCREASE_COLOR = '#ea580c'
const DECREASE_COLOR = '#0369a1'

export default function DeltaBarChart({ countries }: { countries: Country[] }) {
  const top = [...countries].sort((a, b) => Math.abs(b.delta_mw) - Math.abs(a.delta_mw)).slice(0, TOP_N)

  return (
    <Card title="Largest changes" subtitle={`Top ${TOP_N} countries by Δ MW of comparable units`}>
      <div className="p-2 sm:p-4" style={{ height: TOP_N * 26 + 40 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={top} layout="vertical" margin={{ left: 8, right: 56 }}>
            <XAxis type="number" hide domain={['dataMin', 'dataMax']} />
            <YAxis type="category" dataKey="name" width={110} tickLine={false} axisLine={false} fontSize={12} />
            <ReferenceLine x={0} stroke="#d4d4d8" />
            <Tooltip
              formatter={(value) => formatSignedGw(Number(value))}
              cursor={{ fill: '#f4f4f5' }}
              contentStyle={{ fontSize: 12, borderRadius: 8 }}
            />
            <Bar dataKey="delta_mw" name="Δ" isAnimationActive={false}>
              {top.map((c) => (
                <Cell key={c.name} fill={c.delta_mw >= 0 ? INCREASE_COLOR : DECREASE_COLOR} />
              ))}
              <LabelList
                dataKey="delta_mw"
                position="right"
                fontSize={11}
                fill="#71717a"
                formatter={(value) => formatSignedGw(Number(value))}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  )
}
