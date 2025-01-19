FROM caddy:2.9.1-builder AS builder

RUN xcaddy build v2.9.1 \
  --with github.com/mholt/caddy-ratelimit

FROM caddy:2.9.1

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
COPY Caddyfile /etc/caddy/Caddyfile
