'use client';

import { useState } from 'react';
import { RotateCcw } from 'lucide-react';
import TopScorers from '../components/TopScorers';
import LeagueBreakdown from '../components/LeagueBreakdown';
import PointsPerGame from '../components/PointsPerGame';
import GoalsAssistsScatter from '../components/GoalsAssistsScatter';
import PointsByPosition from '../components/PointsByPosition';
import PlusMinusLeaders from '../components/PlusMinusLeaders';
import PlayerTable from '../components/PlayerTable';
import { enrichPlayer } from '../lib/players';
import data from '../data/players.json';

// Data is baked in at build time (exported nightly from MongoDB)
const stats = data.players.map(enrichPlayer);
const leagues = [...new Set(stats.map(p => p.league))].sort();
const season = data.players[0]?.season ?? '';
const updated = data.players.reduce((m, p) => (p.updated_at > m ? p.updated_at : m), '').slice(0, 10);

const DEFAULTS = {
  search: '',
  league: 'All',
  playerType: 'All',
  rankBy: 'tp',
};
const DEFAULT_SORT = { key: 'tp', dir: 'desc' };

const fieldClass =
  'w-full bg-slate-800 border border-white/10 text-white px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400';

function Field({ label, htmlFor, children }) {
  return (
    <div>
      <label htmlFor={htmlFor} className="block text-xs font-semibold uppercase tracking-wide text-slate-400 mb-1.5">
        {label}
      </label>
      {children}
    </div>
  );
}

export default function Dashboard() {
  // Site-wide filter states
  const [search, setSearch] = useState(DEFAULTS.search);
  const [filterLeague, setFilterLeague] = useState(DEFAULTS.league);
  const [filterPlayerType, setFilterPlayerType] = useState(DEFAULTS.playerType);
  const [rankBy, setRankBy] = useState(DEFAULTS.rankBy);
  // Table state
  const [sort, setSort] = useState(DEFAULT_SORT);
  const [showAll, setShowAll] = useState(false);

  const isFiltered =
    search !== DEFAULTS.search ||
    filterLeague !== DEFAULTS.league ||
    filterPlayerType !== DEFAULTS.playerType ||
    rankBy !== DEFAULTS.rankBy ||
    sort.key !== DEFAULT_SORT.key ||
    sort.dir !== DEFAULT_SORT.dir;

  const resetFilters = () => {
    setSearch(DEFAULTS.search);
    setFilterLeague(DEFAULTS.league);
    setFilterPlayerType(DEFAULTS.playerType);
    setRankBy(DEFAULTS.rankBy);
    setSort(DEFAULT_SORT);
    setShowAll(false);
  };

  // "Rank by" drives the Top 10 chart and re-sorts the table on that stat
  const handleRankBy = value => {
    setRankBy(value);
    setSort({ key: value, dir: 'desc' });
  };

  // Apply filters to data
  const filteredStats = stats.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(search.toLowerCase());
    const matchesLeague = filterLeague === 'All' || p.league === filterLeague;

    let matchesPlayerType = true;
    if (filterPlayerType === 'NHL Only') {
      matchesPlayerType = p.league === 'NHL';
    } else if (filterPlayerType === 'Prospects Only') {
      matchesPlayerType = p.league !== 'NHL';
    }

    return matchesSearch && matchesLeague && matchesPlayerType;
  });

  return (
    <div className="min-h-screen bg-[#0a1020] text-white">
      {/* Header */}
      <header className="relative overflow-hidden bg-gradient-to-br from-[#002868] via-[#00337f] to-[#001a45] border-b-4 border-white shadow-lg">
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(circle_at_85%_20%,#ffffff_0,transparent_45%)]" />
        <div className="relative container mx-auto px-6 py-8">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Tampa Bay Lightning Stats</h1>
            <p className="text-blue-100/90 mt-1 text-sm md:text-base">
              Season {season} · {stats.length} players · Updated {updated}
            </p>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 md:px-6 py-6 space-y-6">
        {/* SITE-WIDE FILTERS */}
        <section className="bg-[#121a2c] border border-white/10 rounded-xl p-5 shadow-lg">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
            <h2 className="text-lg font-bold">Filters</h2>
            <button
              type="button"
              onClick={resetFilters}
              disabled={!isFiltered}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-semibold border border-white/20 text-white hover:bg-white/10 disabled:opacity-40 disabled:hover:bg-transparent disabled:cursor-not-allowed cursor-pointer transition-colors"
            >
              <RotateCcw size={14} /> Reset filters
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Field label="Search" htmlFor="f-search">
              <input
                id="f-search"
                type="text"
                placeholder="Player name..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                className={fieldClass}
              />
            </Field>

            <Field label="Player type" htmlFor="f-type">
              <select id="f-type" value={filterPlayerType} onChange={e => setFilterPlayerType(e.target.value)} className={fieldClass}>
                <option value="All">All players</option>
                <option value="NHL Only">NHL only</option>
                <option value="Prospects Only">Prospects only</option>
              </select>
            </Field>

            <Field label="League" htmlFor="f-league">
              <select id="f-league" value={filterLeague} onChange={e => setFilterLeague(e.target.value)} className={fieldClass}>
                <option value="All">All leagues</option>
                {leagues.map(league => (
                  <option key={league} value={league}>{league}</option>
                ))}
              </select>
            </Field>

            <Field label="Rank by" htmlFor="f-rank">
              <select id="f-rank" value={rankBy} onChange={e => handleRankBy(e.target.value)} className={fieldClass}>
                <option value="tp">Points</option>
                <option value="g">Goals</option>
                <option value="a">Assists</option>
                <option value="gp">Games played</option>
              </select>
            </Field>
          </div>

          <p className="text-slate-400 text-sm mt-4">
            Showing {filteredStats.length} of {stats.length} players
          </p>
        </section>

        {/* Player Table */}
        <PlayerTable
          stats={filteredStats}
          sort={sort}
          onSortChange={setSort}
          showAll={showAll}
          onShowAllChange={setShowAll}
        />

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TopScorers stats={filteredStats} rankBy={rankBy} />
          <PointsPerGame stats={filteredStats} />
          <GoalsAssistsScatter stats={filteredStats} />
          <PlusMinusLeaders stats={filteredStats} />
          <PointsByPosition stats={filteredStats} />
          <LeagueBreakdown stats={filteredStats} />
        </div>
      </main>
    </div>
  );
}
