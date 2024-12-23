import { MongoClient } from "mongodb";
import type {
  Fixture,
  GameweekStats,
  HistoryEntry,
  Player,
  PlayerSummary,
  SeasonTotals,
  StatsPerNinety,
} from "../types/player.js";

interface ProcessPlayersResult {
  page: number;
  pageCount: number;
  resultCount: number;
  totalCount: number;
  players: PlayerSummary[];
}

export const processPlayers = async (
  mongoClient: MongoClient,
  queryParams: Record<string, string>
): Promise<ProcessPlayersResult> => {
  const database = mongoClient.db(process.env.DB_NAME);
  const collection = database.collection(process.env.COLLECTION_NAME!);
  const { page, limit, sortBy, order, team, position, maxPrice, minPrice } =
    queryParams;
  let paginationConfig: { page: number; skip: number; limit: number } = {
    page: 1,
    skip: 0,
    limit: 25,
  };

  if (page || limit) {
    let parsedPage;
    if (!Number.isNaN(parseInt(page))) {
      parsedPage = parseInt(page);
    } else {
      parsedPage = 1;
    }

    let parsedLimit;
    if (!Number.isNaN(parseInt(limit))) {
      parsedLimit = parseInt(limit);
    } else {
      parsedLimit = 25;
    }

    paginationConfig = {
      page: parsedPage,
      skip: (parsedPage - 1) * parsedLimit,
      limit: parsedLimit,
    };
  }
  const skip = (parseInt(page) - 1) * parseInt(limit);

  let sortConfig = {};
  if (sortBy) {
    sortConfig = { [sortBy]: order === "asc" ? 1 : -1 };
  }

  let filterConfig = {};
  if (team || position || maxPrice || minPrice) {
    filterConfig = {
      $and: [
        team ? { team: team } : {},
        position ? { position: position } : {},
        maxPrice ? { price: { $lte: parseInt(maxPrice) } } : {},
        minPrice ? { price: { $gte: parseInt(minPrice) } } : {},
      ],
    };
  }

  const players = await collection
    .find(filterConfig, {
      projection: { season_stats: 0, history: 0, fixtures: 0 },
    })
    .sort(sortConfig)
    .skip(paginationConfig.skip)
    .limit(paginationConfig.limit)
    .toArray();

  const totalCount = await collection.countDocuments(filterConfig);
  const pageCount = Math.ceil(totalCount / paginationConfig.limit);

  return {
    page: paginationConfig.page,
    pageCount: pageCount,
    resultCount: players.length,
    totalCount: totalCount,
    players: players.map((dbPlayer) => ToPlayerSummary(dbPlayer)),
  };
};

function ToPlayerSummary(doc: any): PlayerSummary {
  return {
    id: doc._id,
    status: doc.status,
    position: doc.position,
    name: doc.name,
    team: doc.team,
    price: doc.price,
    form: doc.form,
    pointsPerMatch: doc.points_per_match,
    gameweekPoints: doc.gameweek_points,
    totalPoints: doc.total_points,
    totalBonus: doc.total_bonus,
    ictIndex: doc.ict_index,
    tsb: doc.tsb,
    lastUpdated: doc.last_updated,
  };
}

export function ToPlayer(doc: any): Player {
  return {
    id: doc._id,
    status: doc.status,
    position: doc.position,
    name: doc.name,
    team: doc.team,
    price: doc.price,
    form: doc.form,
    pointsPerMatch: doc.points_per_match,
    gameweekPoints: doc.gameweek_points,
    totalPoints: doc.total_points,
    totalBonus: doc.total_bonus,
    ictIndex: doc.ict_index,
    tsb: doc.tsb,
    seasonStats: {
      gameweekStats: doc.season_stats?.gameweek_stats?.map(ToGameweekStats),
      aggregateStats: {
        seasonTotals: ToSeasonTotals(
          doc.season_stats?.aggregate_stats.season_totals
        ),
        statsPerNinety: ToStatsPerNinety(
          doc.season_stats?.aggregate_stats.stats_per_ninety
        ),
      },
    },
    history: doc.history?.map(ToHistoryEntry),
    fixtures: doc.fixtures?.map(ToFixture),
    lastUpdated: doc.last_updated,
  };
}

function ToGameweekStats(gw: any): GameweekStats {
  return {
    gameweek: gw.gameweek,
    opponent: gw.opponent,
    outcome: gw.outcome,
    points: gw.points,
    start: gw.start,
    minutesPlayed: gw.minutes_played,
    goalsScored: gw.goals_scored,
    assists: gw.assists,
    expectedGoals: gw.expected_goals,
    expectedAssists: gw.expected_assists,
    expectedGoalInvolvements: gw.expected_goal_involvements,
    cleanSheets: gw.clean_sheets,
    goalsConceded: gw.goals_conceded,
    expectedGoalsConceded: gw.expected_goals_conceded,
    ownGoals: gw.own_goals,
    penaltiesSaved: gw.penalties_saved,
    penaltiesMissed: gw.penalties_missed,
    yellowCards: gw.yellow_cards,
    redCards: gw.red_cards,
    saves: gw.saves,
    bonusPoints: gw.bonus_points,
    bonusPointsSystem: gw.bonus_points_system,
    influence: gw.influence,
    creativity: gw.creativity,
    threat: gw.threat,
    ictIndex: gw.ict_index,
    nt: gw.nt,
    sb: gw.sb,
    price: gw.price,
  };
}

function ToSeasonTotals(totals: any): SeasonTotals | undefined {
  if (!totals) return undefined;
  return {
    points: totals.points,
    starts: totals.starts,
    minutes: totals.minutes,
    goalsScored: totals.goals_scored,
    assists: totals.assists,
    expectedGoals: totals.expected_goals,
    expectedAssists: totals.expected_assists,
    expectedGoalInvolvements: totals.expected_goal_involvements,
    cleanSheets: totals.clean_sheets,
    goalsConceded: totals.goals_conceded,
    expectedGoalsConceded: totals.expected_goals_conceded,
    ownGoals: totals.own_goals,
    penaltiesSaved: totals.penalties_saved,
    penaltiesMissed: totals.penalties_missed,
    yellowCards: totals.yellow_cards,
    redCards: totals.red_cards,
    saves: totals.saves,
    bonusPoints: totals.bonus_points,
    bonusPointSystem: totals.bonus_point_system,
    influence: totals.influence,
    creativity: totals.creativity,
    threat: totals.threat,
    ictIndex: totals.ict_index,
  };
}

function ToStatsPerNinety(stats: any): StatsPerNinety | undefined {
  if (!stats) return undefined;
  return {
    expectedGoals: stats.expected_goals,
    expectedAssists: stats.expected_assists,
    expectedGoalInvolvements: stats.expected_goal_involvements,
    cleanSheets: stats.clean_sheets,
    goalsConceded: stats.goals_conceded,
    expectedGoalsConceded: stats.expected_goals_conceded,
    saves: stats.saves,
  };
}

function ToHistoryEntry(h: any): HistoryEntry {
  return {
    season: h.season,
    points: h.points,
    gamesStarted: h.games_started,
    minutesPlayed: h.minutes_played,
    goalsScored: h.goals_scored,
    assists: h.assists,
    expectedGoals: h.expected_goals,
    expectedAssists: h.expected_assists,
    expectedGoalInvolvements: h.expected_goal_involvements,
    cleanSheets: h.clean_sheets,
    goalsConceded: h.goals_conceded,
    expectedGoalsConceded: h.expected_goals_conceded,
    ownGoals: h.own_goals,
    penaltiesSaved: h.penalties_saved,
    penaltiesMissed: h.penalties_missed,
    yellowCards: h.yellow_cards,
    redCards: h.red_cards,
    saves: h.saves,
    bonusPoints: h.bonus_points,
    bonusPointsSystem: h.bonus_points_system,
    influence: h.influence,
    creativity: h.creativity,
    threat: h.threat,
    ictIndex: h.ict_index,
    seasonStartPrice: h.season_start_price,
    seasonEndPrice: h.season_end_price,
  };
}

function ToFixture(f: any): Fixture {
  return {
    date: f.date,
    time: f.time,
    gameweek: f.gameweek,
    opponent: f.opponent,
    homeAway: f.home_away,
    difficulty: f.difficulty,
  };
}
