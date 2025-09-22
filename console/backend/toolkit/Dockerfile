FROM artifacts.iflytek.com/cbg-docker-private/xfyun_webdev/maven:3.9.9-eclipse-temurin-21 AS build
WORKDIR /backend

# Copy root and module POMs first for efficient layer caching
COPY pom.xml ./
COPY commons/pom.xml commons/pom.xml
COPY auth/pom.xml auth/pom.xml
COPY hub/pom.xml hub/pom.xml
COPY toolkit/pom.xml toolkit/pom.xml

# Copy full source and build only the hub module (and its dependencies)
COPY . .
RUN mvn -q -DskipTests package -pl toolkit -am

FROM artifacts.iflytek.com/cbg-docker-private/xfyun_webdev/eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /backend/toolkit/target/toolkit-0.0.1.jar /app/app.jar
EXPOSE 25000
ENTRYPOINT ["java","-jar","/app/app.jar"]


