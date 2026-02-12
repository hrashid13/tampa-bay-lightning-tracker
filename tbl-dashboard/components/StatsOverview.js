export default function StatsOverview({ stats }) {
  const nhlPlayers = stats.filter(p => p.league_name === 'NHL').length;
  const prospects = stats.filter(p => p.is_prospect).length;
  const totalGoals = stats.reduce((sum, p) => sum + parseInt(p.stats?.G || 0), 0);
  const totalPoints = stats.reduce((sum, p) => sum + parseInt(p.stats?.TP || 0), 0);

  const cards = [
    { title: 'NHL Roster', value: nhlPlayers, icon: '' },
    { title: 'Prospects', value: prospects, icon: '' },
    { title: 'Total Goals', value: totalGoals, icon: '' },
    { title: 'Total Points', value: totalPoints, icon: '' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map(card => (
        <div key={card.title} className="bg-gray-800 rounded-lg p-6 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">{card.title}</p>
              <p className="text-3xl font-bold mt-2">{card.value}</p>
            </div>
            <div className="text-4xl">{card.icon}</div>
          </div>
        </div>
      ))}
    </div>
  );
}