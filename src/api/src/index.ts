import "dotenv/config";
import { serve } from "@hono/node-server";
import { Hono } from "hono";
import { MongoClient, ObjectId } from "mongodb";

const app = new Hono();

app.get("/", (c) => c.text("Hello Node.js!"));

const connectionString = process.env.CONNECTION_STRING;

if (!connectionString) {
  throw new Error("CONNECTION_STRING is not defined");
}

const client = new MongoClient(connectionString);

app.use("*", async (c, next) => {
  try {
    await client.connect();
    await next();
  } catch (error) {
    console.error("MongoDB connection error:", error);
    return c.json({ error: "Database connection failed" }, 500);
  } finally {
    await client.close();
  }
});

app.get("/players", async (c) => {
  try {
    const database = client.db(process.env.DB_NAME);
    const collection = database.collection(process.env.COLLECTION_NAME!);

    // TODO: Validate query parameters
    const { page, limit, sortBy, order, team, position, maxPrice, minPrice } =
      c.req.query();

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

    return c.json({
      page: paginationConfig.page,
      pageCount,
      resultCount: players?.length ?? 0,
      totalCount,
      players,
    });
  } catch (error) {
    console.error("Error retrieving players:", error);
    return c.json({ error: "Failed to retrieve players" }, 500);
  }
});

app.get("/players/:id", async (c) => {
  try {
    const database = client.db(process.env.DB_NAME);
    const collection = database.collection(process.env.COLLECTION_NAME!);

    const playerId = c.req.param("id");
    const player = await collection.findOne({ _id: new ObjectId(playerId) });

    if (!player) {
      return c.json({ error: "Player not found" }, 404);
    }

    return c.json(player);
  } catch (error) {
    console.error("Error retrieving player:", error);
    return c.json({ error: "Failed to retrieve player" }, 500);
  }
});

serve(app);
