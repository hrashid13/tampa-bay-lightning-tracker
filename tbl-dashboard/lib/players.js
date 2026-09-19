// Shared data helpers and colors for the dashboard.

export const LIGHTNING_BLUE = '#002868';

// Leagues are grouped into families so every chart can keep a small,
// colorblind-safe palette. A league always gets its family's color.
const LEAGUE_FAMILY = {
  NHL: 'NHL',
  AHL: 'AHL',
  NCAA: 'NCAA',
  OHL: 'CHL',
  WHL: 'CHL',
  QMJHL: 'CHL',
  USHL: 'USHL',
  KHL: 'Europe',
  VHL: 'Europe',
  SHL: 'Europe',
  Liiga: 'Europe',
};

// Order matters: validated for CVD separation on the dark card surface.
export const FAMILY_COLORS = {
  NHL: '#3987e5',
  AHL: '#d95926',
  NCAA: '#199e70',
  CHL: '#c98500',
  USHL: '#d55181',
  Europe: '#9085e9',
  Other: '#898781',
};

export const FAMILY_LABELS = {
  NHL: 'NHL',
  AHL: 'AHL',
  NCAA: 'NCAA',
  CHL: 'CHL (OHL/WHL/QMJHL)',
  USHL: 'USHL',
  Europe: 'Europe (KHL/VHL/SHL/Liiga)',
  Other: 'Other',
};

export function leagueFamily(league) {
  return LEAGUE_FAMILY[league] || 'Other';
}

export function leagueColor(league) {
  return FAMILY_COLORS[leagueFamily(league)];
}

// Stats arrive as strings, with "-" when a player has no games yet.
export function num(value) {
  const n = parseFloat(value);
  return Number.isFinite(n) ? n : null;
}

const POSITION_LABELS = {
  C: 'Center',
  LW: 'Left Wing',
  RW: 'Right Wing',
  W: 'Wing',
  F: 'Forward',
  D: 'Defense',
};

export function positionLabel(pos) {
  return POSITION_LABELS[pos] || pos;
}

// "Daniil Pylenkov (D)" -> { name: "Daniil Pylenkov", position: "D", primaryPosition: "D" }
export function parsePlayerName(raw) {
  const match = raw.match(/^(.*?)\s*\(([^)]+)\)\s*$/);
  if (!match) return { name: raw.trim(), position: '', primaryPosition: '' };
  const position = match[2].trim();
  return { name: match[1].trim(), position, primaryPosition: position.split('/')[0] };
}

// Flatten a raw record into the shape the UI works with.
export function enrichPlayer(p) {
  const { name, position, primaryPosition } = parsePlayerName(p.player_name);
  const s = p.stats || {};
  const gp = num(s.GP);
  const tp = num(s.TP);
  return {
    id: p._id,
    name,
    position,
    primaryPosition,
    team: p.team_name,
    league: p.league_name,
    family: leagueFamily(p.league_name),
    isProspect: p.is_prospect,
    gp,
    g: num(s.G),
    a: num(s.A),
    tp,
    pim: num(s.PIM),
    plusMinus: num(s['+/-']),
    ppg: gp && tp !== null ? tp / gp : null,
  };
}

export const STAT_LABELS = {
  tp: 'Points',
  g: 'Goals',
  a: 'Assists',
  gp: 'Games',
  plusMinus: '+/-',
  ppg: 'Points/Game',
  pim: 'PIM',
};

// Short "F. Lastname" label keeps chart axes compact.
export function shortName(name) {
  const parts = name.split(' ');
  if (parts.length < 2) return name;
  return `${parts[0][0]}. ${parts.slice(1).join(' ')}`;
}
