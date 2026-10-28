import { defineConfig } from 'cypress';

export default defineConfig({
    e2e: {
        // Requires the frontend (npm run dev) and backend to be running locally,
        // with the backend configured with OIDC_ENABLED=false (see backend/.env)
        // so requests are auto-authenticated as DEFAULT_USERNAME, and the database
        // seeded via `poetry run python -m app.db_tool init sample_data.sql`.
        baseUrl: 'http://localhost:3000',
        supportFile: 'cypress/support/e2e.ts',
        specPattern: 'cypress/e2e/**/*.cy.ts',
        defaultCommandTimeout: 10000,
    },
});
