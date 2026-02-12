import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function TopScorers({ stats, sortBy = 'TP' }) {
  // Use the sortBy from site-wide filter
  const statKey = sortBy;
  
  const topScorers = stats
    .filter(p => p.stats?.[statKey])
    .sort((a, b) => parseInt(b.stats[statKey]) - parseInt(a.stats[statKey]))
    .slice(0, 10)
    .map(p => ({
      name: p.player_name.split(' ').slice(0, 2).join(' '),
      value: parseInt(p.stats[statKey]),
      league: p.league_name
    }));

  // Dynamic label based on what we're sorting by
  const labels = {
    TP: 'Points',
    G: 'Goals',
    A: 'Assists',
    GP: 'Games'
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
      <h2 className="text-2xl font-bold mb-4">
         Top 10 by {labels[statKey] || 'Points'}
      </h2>
      
      {topScorers.length === 0 ? (
        <div className="text-gray-400 text-center py-8">
          No data available for selected filters
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={topScorers}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="name" 
              angle={-45} 
              textAnchor="end" 
              height={100} 
              stroke="#9CA3AF" 
            />
            <YAxis stroke="#9CA3AF" />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1F2937', border: 'none' }}
              labelStyle={{ color: '#F3F4F6' }}
              formatter={(value, name, props) => [
                `${value} ${labels[statKey]}`,
                props.payload.league
              ]}
            />
            <Bar dataKey="value" fill="#3B82F6" />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}