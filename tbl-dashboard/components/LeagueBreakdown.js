import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, LabelList } from 'recharts';
import ChartCard, { AXIS, GRID, HOVER_CURSOR, EmptyState, TooltipBox, FamilyLegend } from './ChartCard';
import { leagueColor, leagueFamily } from '../lib/players';

export default function LeagueBreakdown({ stats }) {
  const counts = {};
  stats.forEach(p => {
    counts[p.league] = (counts[p.league] || 0) + 1;
  });

  const data = Object.entries(counts)
    .map(([name, value]) => ({ name, value, family: leagueFamily(name) }))
    .sort((a, b) => b.value - a.value || a.name.localeCompare(b.name));

  return (
    <ChartCard title="Players by League" subtitle={`${stats.length} players across ${data.length} leagues`}>
      {data.length === 0 ? (
        <EmptyState />
      ) : (
        <>
          <ResponsiveContainer width="100%" height={data.length * 30 + 30}>
            <BarChart data={data} layout="vertical" margin={{ top: 0, right: 36, left: 0, bottom: 0 }} barCategoryGap={4}>
              <CartesianGrid {...GRID} horizontal={false} />
              <XAxis type="number" allowDecimals={false} {...AXIS} />
              <YAxis type="category" dataKey="name" width={60} {...AXIS} tickLine={false} />
              <Tooltip
                cursor={HOVER_CURSOR}
                content={({ active, payload }) => {
                  if (!active || !payload?.length) return null;
                  const d = payload[0].payload;
                  const pct = Math.round((d.value / stats.length) * 100);
                  return (
                    <TooltipBox title={d.name} color={leagueColor(d.name)} rows={[['Players', d.value], ['Share', `${pct}%`]]} />
                  );
                }}
              />
              <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={22}>
                {data.map(d => <Cell key={d.name} fill={leagueColor(d.name)} />)}
                <LabelList dataKey="value" position="right" fill="#c3c2b7" fontSize={12} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <FamilyLegend families={data.map(d => d.family)} />
        </>
      )}
    </ChartCard>
  );
}
