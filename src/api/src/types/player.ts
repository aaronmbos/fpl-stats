interface Status {
  flag: string;
  reason?: string;
}

export interface GameweekStats {
  gameweek: number;
  opponent: string;
  outcome: string;
  points: number;
  start: number;
  minutesPlayed: number;
  goalsScored: number;
  assists: number;
  expectedGoals: number;
  expectedAssists: number;
  expectedGoalInvolvements: number;
  cleanSheets: number;
  goalsConceded: number;
  expectedGoalsConceded: number;
  ownGoals: number;
  penaltiesSaved: number;
  penaltiesMissed: number;
  yellowCards: number;
  redCards: number;
  saves: number;
  bonusPoints: number;
  bonusPointsSystem: number;
  influence: number;
  creativity: number;
  threat: number;
  ictIndex: number;
  nt: number;
  sb: number;
  price: number;
}

export interface SeasonTotals {
  points: number;
  starts: number;
  minutes: number;
  goalsScored: number;
  assists: number;
  expectedGoals: number;
  expectedAssists: number;
  expectedGoalInvolvements: number;
  cleanSheets: number;
  goalsConceded: number;
  expectedGoalsConceded: number;
  ownGoals: number;
  penaltiesSaved: number;
  penaltiesMissed: number;
  yellowCards: number;
  redCards: number;
  saves: number;
  bonusPoints: number;
  bonusPointSystem: number;
  influence: number;
  creativity: number;
  threat: number;
  ictIndex: number;
}

export interface StatsPerNinety {
  expectedGoals: number;
  expectedAssists: number;
  expectedGoalInvolvements: number;
  cleanSheets: number;
  goalsConceded: number;
  expectedGoalsConceded: number;
  saves: number;
}

export interface AggregateStats {
  seasonTotals?: SeasonTotals;
  statsPerNinety?: StatsPerNinety;
}

export interface SeasonStats {
  gameweekStats: GameweekStats[];
  aggregateStats: AggregateStats;
}

export interface HistoryEntry {
  season: string;
  points: number;
  gamesStarted: number;
  minutesPlayed: number;
  goalsScored: number;
  assists: number;
  expectedGoals: number;
  expectedAssists: number;
  expectedGoalInvolvements: number;
  cleanSheets: number;
  goalsConceded: number;
  expectedGoalsConceded: number;
  ownGoals: number;
  penaltiesSaved: number;
  penaltiesMissed: number;
  yellowCards: number;
  redCards: number;
  saves: number;
  bonusPoints: number;
  bonusPointsSystem: number;
  influence: number;
  creativity: number;
  threat: number;
  ictIndex: number;
  seasonStartPrice: number;
  seasonEndPrice: number;
}

export interface Fixture {
  date: string;
  time: string;
  gameweek: string;
  opponent: string;
  homeAway: string;
  difficulty: number;
}

export type Player = {
  id: string;
  status: Status;
  position: string;
  name: string;
  team: string;
  price: number;
  form: number;
  pointsPerMatch: number;
  gameweekPoints: number;
  totalPoints: number;
  totalBonus: number;
  ictIndex: number;
  tsb: number;
  seasonStats: SeasonStats;
  history: HistoryEntry[];
  fixtures: Fixture[];
  lastUpdated: string;
};

export type PlayerSummary = Omit<
  Player,
  "seasonStats" | "history" | "fixtures"
>;
