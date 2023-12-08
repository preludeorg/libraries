FROM --platform=$BUILDPLATFORM node:18.9-alpine3.15 AS client-builder
WORKDIR /app/client
# cache packages in layer
COPY client/package.json /app/client/package.json
COPY client/yarn.lock /app/client/yarn.lock
ARG TARGETARCH
RUN yarn config set cache-folder /usr/local/share/.cache/yarn-${TARGETARCH}
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn-${TARGETARCH} yarn
# install
COPY client /app/client
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn-${TARGETARCH} yarn build

FROM scratch

LABEL org.opencontainers.image.title="Prelude Detect" \
    org.opencontainers.image.description="Install Prelude probes into running containers" \
    org.opencontainers.image.vendor="Prelude Research, Inc." \
    com.docker.desktop.extension.api.version="0.3.4" \
    com.docker.extension.screenshots="[{\"alt\":\"Marketplace Entry\",\"url\":\"https://files.readme.io/77845d7-CleanShot_2023-06-20_at_16.25.592x.png\"},{\"alt\":\"Extension UI\",\"url\":\"https://files.readme.io/d7e8696-CleanShot_2023-06-20_at_16.27.472x.png\"}]" \
    com.docker.desktop.extension.icon="https://uploads-ssl.webflow.com/63403a034e35d0ce90c01fb1/6491cb89750423dce274f594_Prelude_Logo_Inverse.svg" \
    com.docker.extension.detailed-description="View all available containers on your local system, run probes inside those containers if they have the necessary dependencies." \
    com.docker.extension.publisher-url="https://www.preludesecurity.com" \
    com.docker.extension.additional-urls="[{\"title\":\"Documentation\",\"url\":\"https://docs.preludesecurity.com\"},{\"title\":\"Platform\",\"url\":\"https://platform.preludesecurity.com\"}]" \
    com.docker.extension.categories="security,testing-tools" \
    com.docker.extension.changelog="<p>Extension changelog<ul> <li>Initial release</li></ul></p>"

COPY --from=client-builder /app/client/dist ui
COPY metadata.json .
COPY Prelude.svg .
