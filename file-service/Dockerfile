FROM maven:3.9-eclipse-temurin-17 AS builder

WORKDIR /build

# Copy POM file
COPY pom.xml .

# Download dependencies
RUN mvn dependency:resolve

# Copy source code
COPY src/ src/

# Build application
RUN mvn clean package -DskipTests

# Runtime stage
FROM eclipse-temurin:17-jre-slim

WORKDIR /app

# Create upload directory
RUN mkdir -p /app/uploads

# Copy built jar from builder
COPY --from=builder /build/target/fileservice-1.0.0.jar app.jar

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD java -cp app.jar -Dspring.boot.jsessionid=none \
    org.springframework.boot.loader.launch.PropertiesLauncher \
    || exit 1

# Set environment
ENV FILE_STORAGE_PATH=/app/uploads
ENV PORT=8081

# Run application
CMD ["java", "-jar", "app.jar"]
