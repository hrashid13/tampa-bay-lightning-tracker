import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, LabelList } from 'recharts';
import ChartCard, { AXIS, GRID, HOVER_CURSOR, EmptyState, TooltipBox, FamilyLegend } from './ChartCard';
import { STAT_LABELS, FAMILY_COLORS, shortName } from '../lib/players';

export default function TopScorers({ stats, rankBy = 'tp' }) {
  const label = STAT_LABELS[rankBy] || 'Points';

  // Only players who have actually registered the stat
  const data = stats
    .filter(p => p[rankBy] > 0)
    .sort((a, b) => b[rankBy] - a[rankBy])
    .slice(0, 10)
    .map(p => ({ ...p, label: shortName(p.name), value: p[rankBy] }));

  return (
    <ChartCard title={`Top 10 by ${label}`} subtitle="Players with zero are hidden">
      {data.length === 0 ? (
        <EmptyState />
      ) : (
        <>
          <ResponsiveContainer width="100%" height={data.length * 34 + 30}>
            <BarChart data={data} layout="vertical" margin={{ top: 0, right: 36, left: 0, bottom: 0 }} barCategoryGap={4}>
              <CartesianGrid {...GRID} horizontal={false} />
              <XAxis type="number" allowDecimals={false} {...AXIS} />
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
                      rows={[['Team', `${p.team} (${p.league})`], [label, p.value], ['GP', p.gp ?? '-']]}
                    />
                  );
                }}
              />
              <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={24}>
                {data.map(p => <Cell key={p.id} fill={FAMILY_COLORS[p.family]} />)}
                <LabelList dataKey="value" position="right" fill="#c3c2b7" fontSize={12} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <FamilyLegend families={data.map(p => p.family)} />
        </>
      )}
    </ChartCard>
  );
}
