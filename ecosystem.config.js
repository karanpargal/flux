module.exports = {
  apps: [
    {
      name: "agents-server",
      script: "main.py",
      interpreter: "python3",
      args: "--host 0.0.0.0 --port 8000",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "1G",
      env: {
        PYTHON_ENV: "production",
      },
      error_file: "./logs/err.log",
      out_file: "./logs/out.log",
      log_file: "./logs/combined.log",
      time: true,
    },
  ],
};
