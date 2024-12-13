import "dotenv/config";
import { serve } from "@hono/node-server";
import { Hono } from "hono";
import { MongoClient } from "mongodb";

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
    // Connect to the specific database and collection
    const database = client.db(process.env.DB_NAME);
    const collection = database.collection(process.env.COLLECTION_NAME!);

    const { page, limit } = c.req.query();
    const skip = (parseInt(page) - 1) * parseInt(limit);

    // Retrieve all documents
    const players = await collection
      .find({})
      .skip(skip)
      .limit(parseInt(limit))
      .toArray();

    // Return the documents
    return c.json(players);
  } catch (error) {
    console.error("Error retrieving players:", error);
    return c.json({ error: "Failed to retrieve players" }, 500);
  }
});

serve(app);
