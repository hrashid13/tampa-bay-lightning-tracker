import { ScatterChart, Scatter, XAxis, YAxis, ZAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';
import ChartCard, { AXIS, GRID, EmptyState, TooltipBox, FamilyLegend } from './ChartCard';
import { FAMILY_COLORS } from '../lib/players';

export default function GoalsAssistsScatter({ stats }) {
  const data = stats.filter(p => p.gp > 0 && p.g !== null && p.a !== null);
  const max = Math.max(1, ...data.map(p => Math.max(p.g, p.a)));

  return (
    <ChartCard
      title="Goals vs. Assists"
      subtitle="Bubble size = games played. Above the line: scorers. Below: playmakers."
    >
      {data.length === 0 ? (
        <EmptyState />
      ) : (
        <>
          <ResponsiveContainer width="100%" height={340}>
            <ScatterChart margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
              <CartesianGrid {...GRID} />
              <XAxis
                type="number"
                dataKey="a"
                name="Assists"
                domain={[0, 'auto']}
                allowDecimals={false}
                {...AXIS}
                label={{ value: 'Assists', position: 'insideBottom', offset: -10, fill: '#9a9890', fontSize: 12 }}
              />
              <YAxis
                type="number"
                dataKey="g"
                name="Goals"
                domain={[0, 'auto']}
                allowDecimals={false}
                width={44}
                {...AXIS}
                label={{ value: 'Goals', angle: -90, position: 'insideLeft', offset: 10, fill: '#9a9890', fontSize: 12 }}
              />
              <ZAxis type="number" dataKey="gp" range={[40, 400]} name="GP" />
              {/* Equal goals and assists */}
              <ReferenceLine
                segment={[{ x: 0, y: 0 }, { x: max, y: max }]}
                stroke="#52514e"
                strokeDasharray="4 4"
                ifOverflow="hidden"
              />
              <Tooltip
                cursor={false}
                content={({ active, payload }) => {
                  if (!active || !payload?.length) return null;
                  const p = payload[0].payload;
                  return (
                    <TooltipBox
                      title={p.name}
                      color={FAMILY_COLORS[p.family]}
                      rows={[['Team', `${p.team} (${p.league})`], ['Goals', p.g], ['Assists', p.a], ['GP', p.gp]]}
                    />
                  );
                }}
              />
              <Scatter data={data} fillOpacity={0.8} stroke="#121a2c" strokeWidth={2}>
                {data.map(p => <Cell key={p.id} fill={FAMILY_COLORS[p.family]} />)}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
          <FamilyLegend families={data.map(p => p.family)} />
        </>
      )}
    </ChartCard>
  );
}
