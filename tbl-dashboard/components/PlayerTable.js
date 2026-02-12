export default function PlayerTable({ stats, sortBy, externalSearch, externalFilterLeague, externalFilterPlayerType }) {
  // Sort the already-filtered stats
  const sortedStats = stats
    .filter(p => p.stats?.[sortBy])
    .sort((a, b) => parseInt(b.stats?.[sortBy] || 0) - parseInt(a.stats?.[sortBy] || 0));

  return (
    <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
      <h2 className="text-2xl font-bold mb-4"> Player Statistics</h2>
      
      {/* Show active filters */}
      {(externalSearch || externalFilterLeague !== 'All' || externalFilterPlayerType !== 'All') && (
        <div className="mb-4 flex flex-wrap gap-2">
          <span className="text-gray-400 text-sm">Active filters:</span>
          {externalSearch && (
            <span className="bg-blue-600 px-3 py-1 rounded-full text-xs">
              Search: "{externalSearch}"
            </span>
          )}
          {externalFilterPlayerType !== 'All' && (
            <span className="bg-green-600 px-3 py-1 rounded-full text-xs">
              {externalFilterPlayerType}
            </span>
          )}
          {externalFilterLeague !== 'All' && (
            <span className="bg-purple-600 px-3 py-1 rounded-full text-xs">
              League: {externalFilterLeague}
            </span>
          )}
        </div>
      )}

      {/* Table - NO INPUT FIELDS HERE! */}
      <div className="overflow-x-auto">
        {sortedStats.length === 0 ? (
          <div className="text-gray-400 text-center py-8">
            No players match your filters
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left p-3">Player</th>
                <th className="text-left p-3">Team</th>
                <th className="text-left p-3">League</th>
                <th className="text-center p-3">GP</th>
                <th className="text-center p-3">G</th>
                <th className="text-center p-3">A</th>
                <th className="text-center p-3">TP</th>
                <th className="text-center p-3">+/-</th>
              </tr>
            </thead>
            <tbody>
              {sortedStats.map((player, idx) => (
                <tr key={idx} className="border-b border-gray-700 hover:bg-gray-700 transition-colors">
                  <td className="p-3 font-semibold">{player.player_name}</td>
                  <td className="p-3 text-gray-400">{player.team_name}</td>
                  <td className="p-3">
                    <span className={`px-2 py-1 rounded text-xs ${
                      player.league_name === 'NHL' 
                        ? 'bg-blue-600' 
                        : 'bg-green-600'
                    }`}>
                      {player.league_name}
                    </span>
                  </td>
                  <td className="text-center p-3">{player.stats?.GP || '-'}</td>
                  <td className="text-center p-3">{player.stats?.G || '-'}</td>
                  <td className="text-center p-3">{player.stats?.A || '-'}</td>
                  <td className="text-center p-3 font-bold text-blue-400">{player.stats?.TP || '-'}</td>
                  <td className="text-center p-3">{player.stats?.['+/-'] || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}