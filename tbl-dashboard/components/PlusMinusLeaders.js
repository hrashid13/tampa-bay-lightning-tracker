import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';
import ChartCard, { AXIS, GRID, HOVER_CURSOR, EmptyState, TooltipBox } from './ChartCard';
import { shortName } from '../lib/players';

const POSITIVE = '#3987e5';
const NEGATIVE = '#e66767';
const PER_SIDE = 8;

export default function PlusMinusLeaders({ stats }) {
  const rated = stats.filter(p => p.plusMinus !== null && p.plusMinus !== 0);
  const best = rated.filter(p => p.plusMinus > 0).sort((a, b) => b.plusMinus - a.plusMinus).slice(0, PER_SIDE);
  const worst = rated.filter(p => p.plusMinus < 0).sort((a, b) => b.plusMinus - a.plusMinus).slice(-PER_SIDE);

  const data = [...best, ...worst].map(p => ({ ...p, label: shortName(p.name), value: p.plusMinus }));
  // Symmetric axis around zero, rounded to a clean step
  const rawExtent = Math.max(1, ...data.map(d => Math.abs(d.value)));
  const step = rawExtent > 20 ? 10 : rawExtent > 10 ? 5 : rawExtent > 4 ? 2 : 1;
  const extent = Math.ceil(rawExtent / step) * step;
  const ticks = [];
  for (let t = -extent; t <= extent; t += step * (extent / step > 5 ? 2 : 1)) ticks.push(t);

  return (
    <ChartCard title="+/- Leaders" subtitle={`Top ${PER_SIDE} and bottom ${PER_SIDE}, excluding even players`}>
      {data.length === 0 ? (
        <EmptyState />
      ) : (
        <>
          <ResponsiveContainer width="100%" height={data.length * 28 + 30}>
            <BarChart data={data} layout="vertical" margin={{ top: 0, right: 20, left: 0, bottom: 0 }} barCategoryGap={3}>
              <CartesianGrid {...GRID} horizontal={false} />
              <XAxis type="number" domain={[-extent, extent]} ticks={ticks} allowDecimals={false} {...AXIS} />
              <YAxis type="category" dataKey="label" width={130} {...AXIS} tickLine={false} />
              <ReferenceLine x={0} stroke="#6b6a64" />
              <Tooltip
                cursor={HOVER_CURSOR}
                content={({ active, payload }) => {
                  if (!active || !payload?.length) return null;
                  const p = payload[0].payload;
                  return (
                    <TooltipBox
                      title={p.name}
                      color={p.value > 0 ? POSITIVE : NEGATIVE}
                      rows={[['Team', `${p.team} (${p.league})`], ['+/-', p.value > 0 ? `+${p.value}` : p.value], ['GP', p.gp]]}
                    />
                  );
                }}
              />
              <Bar dataKey="value" maxBarSize={20}>
                {data.map(p => (
                  <Cell key={p.id} fill={p.value > 0 ? POSITIVE : NEGATIVE} radius={p.value > 0 ? [0, 4, 4, 0] : [4, 0, 0, 4]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="flex gap-4 mt-3 text-xs text-slate-300">
            <span className="flex items-center gap-1.5">
              <span className="inline-block w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: POSITIVE }} /> Plus
            </span>
            <span className="flex items-center gap-1.5">
              <span className="inline-block w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: NEGATIVE }} /> Minus
            </span>
          </div>
        </>
      )}
    </ChartCard>
  );
}
