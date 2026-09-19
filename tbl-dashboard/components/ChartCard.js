import { FAMILY_COLORS, FAMILY_LABELS } from '../lib/players';

// Shared chart chrome so every chart reads as one system.
export const AXIS = { stroke: '#383835', tick: { fill: '#9a9890', fontSize: 12 } };
export const GRID = { stroke: '#2c2c2a', strokeDasharray: '0' };
export const HOVER_CURSOR = { fill: 'rgba(255,255,255,0.05)' };

export default function ChartCard({ title, subtitle, controls, children }) {
  return (
    <section className="bg-[#121a2c] border border-white/10 rounded-xl p-5 shadow-lg flex flex-col">
      <div className="flex flex-wrap items-start justify-between gap-3 mb-4">
        <div>
          <h2 className="text-lg font-bold text-white">{title}</h2>
          {subtitle && <p className="text-sm text-slate-400 mt-0.5">{subtitle}</p>}
        </div>
        {controls}
      </div>
      <div className="flex-1">{children}</div>
    </section>
  );
}

export function EmptyState({ children = 'No data for the selected filters' }) {
  return <div className="text-slate-400 text-center py-12 text-sm">{children}</div>;
}

// Dark tooltip: title line plus label/value rows. Text stays in ink colors;
// a small swatch carries identity.
export function TooltipBox({ title, rows, color }) {
  return (
    <div className="bg-[#0b1020] border border-white/15 rounded-lg px-3 py-2 shadow-xl text-sm">
      <div className="flex items-center gap-2 font-semibold text-white mb-1">
        {color && <span className="inline-block w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: color }} />}
        {title}
      </div>
      {rows.map(([label, value]) => (
        <div key={label} className="flex justify-between gap-4 text-slate-300">
          <span className="text-slate-400">{label}</span>
          <span className="tabular-nums">{value}</span>
        </div>
      ))}
    </div>
  );
}

// Legend listing only the league families present in the chart.
export function FamilyLegend({ families }) {
  const present = Object.keys(FAMILY_COLORS).filter(f => families.includes(f));
  if (present.length < 2) return null;
  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1 mt-3 text-xs text-slate-300">
      {present.map(f => (
        <span key={f} className="flex items-center gap-1.5">
          <span className="inline-block w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: FAMILY_COLORS[f] }} />
          {FAMILY_LABELS[f]}
        </span>
      ))}
    </div>
  );
}
