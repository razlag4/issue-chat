module.exports = {
  apps: [
    {
      name: "web",
      script: "server.js",
      interpreter: "node"
    },
    {
      name: "bot",
      script: "docs/bot.py",
      interpreter: "python3"
    },
    {
      name: "iventbot",
      script: "iventbot/iventsbot.py",
      interpreter: "python3"
    }
  ]
}