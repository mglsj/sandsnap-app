FROM oven/bun:1 AS base

FROM base AS install
WORKDIR /app
COPY . .
RUN bun install
RUN bun run build

FROM base AS production
WORKDIR /app
COPY --from=install /app/dist .
ENV NODE_ENV=production HOST=0.0.0.0 PORT=80
CMD ["bun", "run", "./dist/server/entry.mjs"]



