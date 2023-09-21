ARG JDK_VER="17.0.7"

FROM bellsoft/liberica-openjdk-alpine:${JDK_VER}

WORKDIR /app
RUN ["chown", "1000:1000", "."]
USER 1000:1000
