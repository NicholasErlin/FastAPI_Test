ARG JDK_VER="17.0.7"

FROM bellsoft/liberica-openjdk-alpine:${JDK_VER} AS builder

WORKDIR /app
RUN ["chown", "1000:1000", "."]
USER 1000:1000

COPY --chown=1000:1000 gradle/ gradle/
COPY --chown=1000:1000 gradlew build.gradle.kts settings.gradle.kts ./
RUN ./gradlew dependencies

COPY --chown=1000:1000 src/ src/
RUN ./gradlew bootJar -P customArchiveFileName=app.jar


FROM bellsoft/liberica-openjdk-alpine:${JDK_VER}

WORKDIR /app
RUN ["chown", "1000:1000", "."]
USER 1000:1000

COPY --from=builder /app/build/libs/app.jar .

ENTRYPOINT ["java", "-jar", "app.jar"]
