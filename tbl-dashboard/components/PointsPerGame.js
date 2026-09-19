import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, LabelList } from 'recharts';
import ChartCard, { AXIS, GRID, HOVER_CURSOR, EmptyState, TooltipBox, FamilyLegend } from './ChartCard';
import { FAMILY_COLORS, shortName } from '../lib/players';

const MIN_GP_OPTIONS = [1, 5, 10, 20, 40];

export default function PointsPerGame({ stats }) {
  const [minGp, setMinGp] = useState(10);

  const data = stats
    .filter(p => p.gp >= minGp && p.ppg > 0)
    .sort((a, b) => b.ppg - a.ppg)
    .slice(0, 10)
    .map(p => ({ ...p, label: shortName(p.name), value: Number(p.ppg.toFixed(2)) }));

  const controls = (
    <label className="flex items-center gap-2 text-sm text-slate-300">
      Min GP
      <select
        value={minGp}
        onChange={e => setMinGp(Number(e.target.value))}
        className="bg-slate-800 border border-white/10 text-white rounded px-2 py-1"
      >
        {MIN_GP_OPTIONS.map(n => <option key={n} value={n}>{n}</option>)}
      </select>
    </label>
  );

  return (
    <ChartCard title="Points per Game Leaders" subtitle={`Top 10, minimum ${minGp} games played`} controls={controls}>
      {data.length === 0 ? (
        <EmptyState>No players with {minGp}+ games for the selected filters</EmptyState>
      ) : (
        <>
          <ResponsiveContainer width="100%" height={data.length * 34 + 30}>
            <BarChart data={data} layout="vertical" margin={{ top: 0, right: 40, left: 0, bottom: 0 }} barCategoryGap={4}>
              <CartesianGrid {...GRID} horizontal={false} />
              <XAxis type="number" {...AXIS} />
              <YAxis type="category" dataKey="label" width={130} {...AXIS} tickLine={false} />
              <Tooltip
                cursor={HOVER_CURSOR}
                content={({ active, payload }) => {
                  if (!active || !payload?.length) return null;
                  const p = payload[0].payload;
                  return (
                    <TooltipBox
                      title={p.name}
                      color={FAMILY_COLORS[p.family]}
                      rows={[['Team', `${p.team} (${p.league})`], ['Points/Game', p.value.toFixed(2)], ['Points', p.tp], ['GP', p.gp]]}
                    />
                  );
                }}
              />
              <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={24}>
                {data.map(p => <Cell key={p.id} fill={FAMILY_COLORS[p.family]} />)}
                <LabelList dataKey="value" position="right" fill="#c3c2b7" fontSize={12} formatter={v => v.toFixed(2)} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <FamilyLegend families={data.map(p => p.family)} />
        </>
      )}
    </ChartCard>
  );
}
