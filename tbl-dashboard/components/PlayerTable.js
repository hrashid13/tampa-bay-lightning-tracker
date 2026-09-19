import { ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-react';
import { leagueColor } from '../lib/players';

const PAGE_SIZE = 20;

const COLUMNS = [
  { key: 'name', label: 'Player', align: 'left', text: true },
  { key: 'position', label: 'Pos', align: 'left', text: true },
  { key: 'team', label: 'Team', align: 'left', text: true },
  { key: 'league', label: 'League', align: 'left', text: true },
  { key: 'gp', label: 'GP', align: 'center' },
  { key: 'g', label: 'G', align: 'center' },
  { key: 'a', label: 'A', align: 'center' },
  { key: 'tp', label: 'TP', align: 'center' },
  { key: 'ppg', label: 'P/GP', align: 'center' },
  { key: 'plusMinus', label: '+/-', align: 'center' },
  { key: 'pim', label: 'PIM', align: 'center' },
];

function compare(a, b, key, dir) {
  const av = a[key];
  const bv = b[key];
  // Players without the stat always sink to the bottom
  const aMissing = av === null || av === undefined || av === '';
  const bMissing = bv === null || bv === undefined || bv === '';
  if (aMissing || bMissing) return aMissing === bMissing ? 0 : aMissing ? 1 : -1;
  const result = typeof av === 'string' ? av.localeCompare(bv) : av - bv;
  return dir === 'asc' ? result : -result;
}

function formatCell(player, key) {
  const v = player[key];
  if (v === null || v === undefined || v === '') return '-';
  if (key === 'ppg') return v.toFixed(2);
  if (key === 'plusMinus' && v > 0) return `+${v}`;
  return v;
}

export default function PlayerTable({ stats, sort, onSortChange, showAll, onShowAllChange }) {
  const sorted = [...stats].sort(
    (a, b) => compare(a, b, sort.key, sort.dir) || compare(a, b, 'tp', 'desc') || a.name.localeCompare(b.name)
  );
  const visible = showAll ? sorted : sorted.slice(0, PAGE_SIZE);

  const handleSort = col => {
    if (sort.key === col.key) {
      onSortChange({ key: col.key, dir: sort.dir === 'asc' ? 'desc' : 'asc' });
    } else {
      // Text columns start A→Z, stat columns start highest first
      onSortChange({ key: col.key, dir: col.text ? 'asc' : 'desc' });
    }
  };

  return (
    <section className="bg-[#121a2c] border border-white/10 rounded-xl shadow-lg">
      <div className="flex flex-wrap items-baseline justify-between gap-2 px-5 pt-5 pb-3">
        <h2 className="text-xl font-bold text-white">Player Statistics</h2>
        <p className="text-sm text-slate-400">
          Showing {visible.length} of {sorted.length} players · click a column to sort
        </p>
      </div>

      {sorted.length === 0 ? (
        <div className="text-slate-400 text-center py-12 text-sm">No players match your filters</div>
      ) : (
        <>
          <div className={`overflow-auto ${showAll ? 'max-h-[75vh]' : ''}`}>
            <table className="w-full text-sm">
              <thead className="sticky top-0 z-10 bg-[#002868] text-white">
                <tr>
                  {COLUMNS.map(col => {
                    const active = sort.key === col.key;
                    const Icon = !active ? ChevronsUpDown : sort.dir === 'asc' ? ChevronUp : ChevronDown;
                    return (
                      <th
                        key={col.key}
                        aria-sort={active ? (sort.dir === 'asc' ? 'ascending' : 'descending') : 'none'}
                        className={`p-0 font-semibold whitespace-nowrap ${col.align === 'center' ? 'text-center' : 'text-left'}`}
                      >
                        <button
                          type="button"
                          onClick={() => handleSort(col)}
                          className={`w-full px-3 py-3 flex items-center gap-1 hover:bg-white/10 transition-colors cursor-pointer ${
                            col.align === 'center' ? 'justify-center' : ''
                          } ${active ? 'text-white' : 'text-blue-100'}`}
                        >
                          {col.label}
                          <Icon size={14} className={active ? 'opacity-100' : 'opacity-40'} />
                        </button>
                      </th>
                    );
                  })}
                </tr>
              </thead>
              <tbody>
                {visible.map(player => {
                  const color = leagueColor(player.league);
                  return (
                    <tr key={player.id} className="border-b border-white/5 odd:bg-white/[0.02] hover:bg-[#1d3a73]/60 transition-colors">
                      <td className="px-3 py-2.5 font-semibold text-white whitespace-nowrap">{player.name}</td>
                      <td className="px-3 py-2.5 text-slate-300">{player.position || '-'}</td>
                      <td className="px-3 py-2.5 text-slate-400 whitespace-nowrap">{player.team}</td>
                      <td className="px-3 py-2.5">
                        <span
                          className="inline-block px-2 py-0.5 rounded text-xs font-semibold border"
                          style={{ backgroundColor: `${color}26`, borderColor: `${color}80`, color: '#fff' }}
                        >
                          {player.league}
                        </span>
                      </td>
                      {COLUMNS.slice(4).map(col => (
                        <td
                          key={col.key}
                          className={`px-3 py-2.5 text-center tabular-nums ${
                            col.key === 'tp' ? 'font-bold text-white' : 'text-slate-300'
                          } ${sort.key === col.key ? 'bg-white/[0.04]' : ''}`}
                        >
                          {formatCell(player, col.key)}
                        </td>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {sorted.length > PAGE_SIZE && (
            <div className="flex justify-center p-4 border-t border-white/5">
              <button
                type="button"
                onClick={() => onShowAllChange(!showAll)}
                className="px-5 py-2 rounded-lg bg-[#002868] hover:bg-[#003a94] border border-white/20 text-white font-semibold text-sm transition-colors cursor-pointer"
              >
                {showAll ? `Show top ${PAGE_SIZE}` : `Show more (${sorted.length - PAGE_SIZE} more)`}
              </button>
            </div>
          )}
        </>
      )}
    </section>
  );
}
