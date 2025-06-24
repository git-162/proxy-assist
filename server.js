// Load environment variables
require("dotenv").config();

// Import dependencies
const express = require("express");
const fetch = require("node-fetch");
const cors = require("cors");

// Create Express app
const app = express();
app.use(cors());
app.use(express.json());

// Confirm API key is loaded
console.log("Loaded API key:", process.env.OPENAI_API_KEY ? "✅" : "❌");

// Chat API endpoint
app.post("/api/chat", async (req, res) => {
  const userMessage = req.body.message;

  try {
    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${process.env.OPENAI_API_KEY}`
      },
      body: JSON.stringify({
        model: "gpt-3.5-turbo",
        messages: [{ role: "user", content: userMessage }],
        max_tokens: 100
      })
    });

    const data = await response.json();

    if (!response.ok) {
      console.error("❌ OpenAI API Error:", data);
      return res.status(500).json({ error: data.error?.message || "Unknown OpenAI error" });
    }

    const reply = data.choices[0]?.message?.content;
    res.json({ reply });

} catch (err) {
  console.error("❌ Server error:", err); // ← log full error
  res.status(500).json({ error: "Server-side failure" });
}
});

// Start server
app.listen(3000, () => {
  console.log("🚀 Server running on http://localhost:3000");
});
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});

