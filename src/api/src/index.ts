import "dotenv/config";
import { serve } from "@hono/node-server";
import { Hono } from "hono";
import { MongoClient, ObjectId } from "mongodb";
import { processPlayers } from "./routeProcessors/playerRoutes.js";

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
    const result = await processPlayers(client, c.req.query());

    return c.json(result);
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
