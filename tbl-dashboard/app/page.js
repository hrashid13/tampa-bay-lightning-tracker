'use client';

import { useState, useEffect } from 'react';
import TopScorers from '../components/TopScorers';
import LeagueBreakdown from '../components/LeagueBreakdown';
import PlayerTable from '../components/PlayerTable';

export default function Dashboard() {
  const [stats, setStats] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Site-wide filter states
  const [search, setSearch] = useState('');
  const [filterLeague, setFilterLeague] = useState('All');
  const [filterPlayerType, setFilterPlayerType] = useState('All');
  const [sortBy, setSortBy] = useState('TP');

  useEffect(() => {
    fetch('/api/stats')
      .then(res => res.json())
      .then(data => {
        setStats(data.stats);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-2xl">Loading...</div>
      </div>
    );
  }

  // Get unique leagues for dropdown
  const leagues = ['All', ...new Set(stats.map(p => p.league_name))];

  // Apply filters to data
  const filteredStats = stats.filter(p => {
    const matchesSearch = p.player_name.toLowerCase().includes(search.toLowerCase());
    const matchesLeague = filterLeague === 'All' || p.league_name === filterLeague;
    
    let matchesPlayerType = true;
    if (filterPlayerType === 'NHL Only') {
      matchesPlayerType = p.league_name === 'NHL';
    } else if (filterPlayerType === 'Prospects Only') {
      matchesPlayerType = p.league_name !== 'NHL';
    }
    
    return matchesSearch && matchesLeague && matchesPlayerType;
  });

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-blue-600 p-6 shadow-lg">
        <h1 className="text-4xl font-bold"> Tampa Bay Lightning Stats</h1>
        <p className="text-blue-100 mt-2">
          Season 2025-2026 • {stats.length} Players
        </p>
      </header>

      {/* Dashboard Content */}
      <div className="container mx-auto p-6">
        
        {/* SITE-WIDE FILTERS */}
        <div className="bg-gray-800 rounded-lg p-6 shadow-lg mb-6">
          <h2 className="text-xl font-bold mb-4"> Filters</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Search Box */}
            <input
              type="text"
              placeholder="Search players..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-gray-700 text-white px-4 py-2 rounded w-full"
            />
            
            {/* Player Type Filter */}
            <select
              value={filterPlayerType}
              onChange={(e) => setFilterPlayerType(e.target.value)}
              className="bg-gray-700 text-white px-4 py-2 rounded"
            >
              <option value="All">All Players</option>
              <option value="NHL Only">NHL Only</option>
              <option value="Prospects Only">Prospects Only</option>
            </select>
            
            {/* League Filter */}
            <select
              value={filterLeague}
              onChange={(e) => setFilterLeague(e.target.value)}
              className="bg-gray-700 text-white px-4 py-2 rounded"
            >
              {leagues.map(league => (
                <option key={league} value={league}>{league}</option>
              ))}
            </select>
            
            {/* Sort By */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-gray-700 text-white px-4 py-2 rounded"
            >
              <option value="TP">Sort by Points</option>
              <option value="G">Sort by Goals</option>
              
              <option value="GP">Sort by Games</option>
            </select>
          </div>

          {/* Results Count */}
          <p className="text-gray-400 text-sm mt-4">
            Showing {filteredStats.length} of {stats.length} players
          </p>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <TopScorers stats={filteredStats} sortBy={sortBy} />
          <LeagueBreakdown stats={filteredStats} />
        </div>

        {/* Player Table */}
        <div>
          <PlayerTable 
            stats={filteredStats} 
            sortBy={sortBy}
            // Pass the filter states so table knows what's selected
            externalSearch={search}
            externalFilterLeague={filterLeague}
            externalFilterPlayerType={filterPlayerType}
          />
        </div>
      </div>
    </div>
  );
}