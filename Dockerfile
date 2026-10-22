FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
COPY apps/api/package.json apps/api/package.json
COPY apps/web/package.json apps/web/package.json
RUN npm install --no-audit --no-fund
COPY apps/ apps/
RUN npm run build
FROM node:22-alpine
ENV NODE_ENV=production PORT=8080
WORKDIR /app
COPY --from=build /app/package*.json ./
COPY --from=build /app/apps/api/package.json apps/api/package.json
COPY --from=build /app/apps/web/package.json apps/web/package.json
# Install only application runtime dependencies. The Node official image bundles
# npm tooling that is not required to execute Quorivio; keeping it increases
# the runtime attack surface and can introduce avoidable CVEs.
RUN npm install --omit=dev --no-audit --no-fund \
    && npm cache clean --force \
    && rm -rf /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/corepack \
              /usr/local/bin/npm /usr/local/bin/npx /usr/local/bin/corepack \
              /root/.npm /tmp/* \
    && test ! -e /usr/local/lib/node_modules/npm \
    && test ! -e /usr/local/bin/npm
COPY --from=build /app/apps/api/dist apps/api/dist
COPY --from=build /app/apps/api/src/schema.sql apps/api/src/schema.sql
COPY --from=build /app/apps/web/dist apps/web/dist
USER node
EXPOSE 8080
CMD ["node","apps/api/dist/server.js"]
