import { serve } from "@hono/node-server";
import { Hono } from "hono";

const app = new Hono();

app.get("/", (c) => c.text("Hello Node.js!"));

app.get("/players", (c) => c.text("Player data"));

serve(app);
