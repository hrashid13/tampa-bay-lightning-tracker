import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LabelList } from 'recharts';
import ChartCard, { AXIS, GRID, HOVER_CURSOR, EmptyState, TooltipBox } from './ChartCard';
import { positionLabel } from '../lib/players';

const GOALS_COLOR = '#3987e5';
const ASSISTS_COLOR = '#86b6ef';

export default function PointsByPosition({ stats }) {
  const groups = {};
  stats
    .filter(p => p.primaryPosition && p.tp !== null)
    .forEach(p => {
      const key = p.primaryPosition;
      groups[key] ??= { pos: key, label: positionLabel(key), g: 0, a: 0, tp: 0, players: 0 };
      groups[key].g += p.g || 0;
      groups[key].a += p.a || 0;
      groups[key].tp += p.tp || 0;
      groups[key].players += 1;
    });

  const data = Object.values(groups)
    .filter(d => d.tp > 0)
    .sort((a, b) => b.tp - a.tp);

  return (
    <ChartCard title="Points by Position" subtitle="Primary listed position, split into goals and assists">
      {data.length === 0 ? (
        <EmptyState />
      ) : (
        <>
          <ResponsiveContainer width="100%" height={data.length * 40 + 30}>
            <BarChart data={data} layout="vertical" margin={{ top: 0, right: 44, left: 0, bottom: 0 }} barCategoryGap={6}>
              <CartesianGrid {...GRID} horizontal={false} />
              <XAxis type="number" allowDecimals={false} {...AXIS} />
              <YAxis type="category" dataKey="label" width={90} {...AXIS} tickLine={false} />
              <Tooltip
                cursor={HOVER_CURSOR}
                content={({ active, payload }) => {
                  if (!active || !payload?.length) return null;
                  const d = payload[0].payload;
                  return (
                    <TooltipBox
                      title={`${d.label} (${d.pos})`}
                      rows={[
                        ['Goals', d.g],
                        ['Assists', d.a],
                        ['Points', d.tp],
                        ['Players', d.players],
                        ['Pts / player', (d.tp / d.players).toFixed(1)],
                      ]}
                    />
                  );
                }}
              />
              <Bar dataKey="g" name="Goals" stackId="pts" fill={GOALS_COLOR} stroke="#121a2c" strokeWidth={2} maxBarSize={26} />
              <Bar dataKey="a" name="Assists" stackId="pts" fill={ASSISTS_COLOR} stroke="#121a2c" strokeWidth={2} radius={[0, 4, 4, 0]} maxBarSize={26}>
                <LabelList dataKey="tp" position="right" fill="#c3c2b7" fontSize={12} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="flex gap-4 mt-3 text-xs text-slate-300">
            <span className="flex items-center gap-1.5">
              <span className="inline-block w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: GOALS_COLOR }} /> Goals
            </span>
            <span className="flex items-center gap-1.5">
              <span className="inline-block w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: ASSISTS_COLOR }} /> Assists
            </span>
          </div>
        </>
      )}
    </ChartCard>
  );
}
