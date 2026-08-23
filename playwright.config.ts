import path from "node:path";
import { defineConfig, devices } from "@playwright/test";

const rootDir = __dirname;
const frontendUrl = process.env.E2E_FRONTEND_URL ?? "http://127.0.0.1:3100";
const backendUrl = process.env.E2E_BACKEND_URL ?? "http://127.0.0.1:8100";
const databasePath = path.resolve(rootDir, "backend", "data", "zemazap_e2e.sqlite3");
const databaseUrl = `sqlite:///${databasePath.replace(/\\/g, "/")}`;
const pythonExecutable =
  process.env.E2E_PYTHON ??
  path.resolve(rootDir, ".venv", process.platform === "win32" ? "Scripts/python.exe" : "bin/python");
const nextExecutable = path.resolve(rootDir, "node_modules", "next", "dist", "bin", "next");
const inheritedEnvironment = Object.fromEntries(
  Object.entries(process.env).filter((entry): entry is [string, string] => typeof entry[1] === "string")
);
const quote = (value: string) => `"${value.replace(/"/g, '\\"')}"`;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: [["list"], ["html", { open: "never" }]],
  outputDir: "test-results/playwright",
  use: {
    baseURL: frontendUrl,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "retain-on-failure"
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] }
    }
  ],
  webServer: [
    {
      command: `${quote(pythonExecutable)} ${quote(path.resolve(rootDir, "scripts", "e2e_backend.py"))}`,
      url: `${backendUrl}/api/health`,
      timeout: 120_000,
      reuseExistingServer: false,
      env: {
        ...inheritedEnvironment,
        DATABASE_URL: databaseUrl,
        E2E_DATABASE_PATH: databasePath,
        DJANGO_DEBUG: "true",
        DJANGO_ALLOWED_HOSTS: "127.0.0.1,localhost",
        DJANGO_CORS_ALLOWED_ORIGINS: frontendUrl,
        DJANGO_CSRF_TRUSTED_ORIGINS: frontendUrl,
        ZEMAZAP_SITE_URL: frontendUrl,
        PAYMENTS_ENABLED: "false",
        PAYMENTS_MODE: "test",
        PAYMENTS_PROVIDER: "alfa",
        FISCALIZATION_ENABLED: "false",
        FISCAL_PROVIDER: "mock",
        ZEMAZAP_MANAGER_EMAIL: "",
        ZEMAZAP_SMTP_HOST: "",
        ZEMAZAP_SMTP_USER: "",
        ZEMAZAP_SMTP_PASSWORD: "",
        ZEMAZAP_TELEGRAM_BOT_TOKEN: "",
        ZEMAZAP_TELEGRAM_CHAT_ID: "",
        PII_IN_NOTIFICATIONS_ALLOWED: "false",
        E2E_ADMIN_USERNAME: "e2e_admin",
        E2E_ADMIN_PASSWORD: "zemazap-e2e-only"
      }
    },
    {
      command: `${quote(process.execPath)} ${quote(nextExecutable)} dev --hostname 127.0.0.1 --port 3100`,
      url: frontendUrl,
      timeout: 120_000,
      reuseExistingServer: false,
      env: {
        ...inheritedEnvironment,
        NEXT_TELEMETRY_DISABLED: "1",
        ZEMAZAP_DJANGO_API_URL: backendUrl,
        ZEMAZAP_DJANGO_PUBLIC_URL: backendUrl,
        ZEMAZAP_SITE_URL: frontendUrl,
        ZEMAZAP_INDEXING_ALLOWED: "false"
      }
    }
  ]
});
