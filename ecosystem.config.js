module.exports = {
  apps: [{
    name: "discord-docs-bot",
    script: "main.py",
    interpreter: "python3",
    cwd: "/opt/discord-docs-bot",  // À modifier selon votre installation

    // Restart automatique
    autorestart: true,
    watch: false,
    max_memory_restart: "500M",
    restart_delay: 5000,

    // Logs
    error_file: "./logs/error.log",
    out_file: "./logs/out.log",
    merge_logs: true,
    log_date_format: "YYYY-MM-DD HH:mm:ss",

    // Environnement
    env: {
      NODE_ENV: "production"
    }
  }]
}
