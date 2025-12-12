FROM node:latest AS base

FROM base AS install
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build

FROM base AS production
WORKDIR /app
COPY .env .
COPY --from=install /app/dist .
COPY package.json .
RUN npm install --production
ENV NODE_ENV=production HOST=0.0.0.0 PORT=80
CMD ["node", "server/entry.mjs"]



