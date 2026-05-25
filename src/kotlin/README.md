# PolyBus Kotlin

A Kotlin implementation of the PolyBus messaging library, providing a unified interface for message transport across different messaging systems.

## Prerequisites

- [JDK 17](https://adoptium.net/) or later
- [Gradle](https://gradle.org/install/) (if you are not using a Gradle wrapper)
- Any IDE that supports Kotlin/JVM development (IntelliJ IDEA, VS Code, Android Studio)

## Quick Start

### Building the Project

```bash
# Navigate to the kotlin directory
cd src/kotlin

# Build the project
gradle build
```

### Running Tests

```bash
# Run all tests
gradle test

# Force all tests to run even if Gradle considers them up-to-date
gradle test --rerun-tasks

# Run checks (includes tests)
gradle check

# Run tests with detailed output
gradle test --info
```

Note: `gradle test` may finish very quickly when the `test` task is up-to-date.
That means Gradle reused previous test results instead of re-running tests.
Use `gradle test --rerun-tasks` (or `gradle clean test`) when you want a full re-run.

### Generating Coverage (Codecov XML)

Codecov accepts JaCoCo XML reports. This project generates that format via Gradle.

```bash
# Run tests and produce coverage reports (XML + HTML)
gradle coverage

# Equivalent explicit command
gradle test jacocoTestReport
```

Coverage report output files:
- XML (for Codecov): `build/reports/jacoco/test/jacocoTestReport.xml`
- HTML (local viewing): `build/reports/jacoco/test/html/index.html`

If you only need to regenerate coverage from a fresh run:

```bash
gradle clean coverage
```

### Running Specific Tests

```bash
# Run one test class
gradle test --tests "polybus.transport.inmemory.InMemoryTransportTests"

# Run tests matching a name pattern
gradle test --tests "*JsonHandlersTests*"
```

## Development Workflow

### Code Quality and Validation

This module uses Kotlin and Gradle defaults with JUnit 5 test execution:

```bash
# Clean build artifacts
gradle clean

# Compile and run all checks
gradle build

# Run only verification lifecycle tasks
gradle check

# Run tests only
gradle test

# Force test re-run (ignores up-to-date optimization)
gradle test --rerun-tasks

# Run tests and generate Codecov-compatible XML coverage
gradle coverage
```

### IDE Integration

#### Visual Studio Code
1. Install the Kotlin extension and Java Extension Pack
2. Open the `src/kotlin` folder in VS Code
3. Use the Java/Kotlin test explorer to run and debug tests
4. Use Problems panel output for compile and test failures

#### IntelliJ IDEA / Android Studio
1. Open the `src/kotlin` folder as a Gradle project
2. Let Gradle import and resolve dependencies
3. Run tests from the gutter or the Gradle tool window

## Configuration

### Build Configuration

The project is configured with Gradle Kotlin DSL (`build.gradle.kts`):

- **Kotlin Plugin**: `org.jetbrains.kotlin.jvm` 2.1.10
- **Java Toolchain**: JDK 17
- **Test Platform**: JUnit 5 (`useJUnitPlatform()`)
- **Project Name**: `Poly.Bus`

### Source Layout

- Main sources: `src/main/kotlin/polybus/`
- Tests: `src/test/kotlin/polybus/`

Core areas in this module include:
- Bus APIs and builders (`IPolyBus`, `PolyBus`, `PolyBusBuilder`)
- Transport abstractions and in-memory transport
- Transaction and message models
- Handler pipeline and JSON serializers

## Dependencies

### Main
- `org.jetbrains.kotlinx:kotlinx-coroutines-core` (1.10.2)
- `com.fasterxml.jackson.core:jackson-databind` (2.18.2)
- `com.fasterxml.jackson.module:jackson-module-kotlin` (2.18.2)

### Test
- `org.jetbrains.kotlin:kotlin-test` (via Kotlin plugin)
- `org.junit.jupiter:junit-jupiter` (5.11.4)

## Common Commands

```bash
# Clean all generated files
gradle clean

# Compile main source
gradle compileKotlin

# Compile tests
gradle compileTestKotlin

# Run all tests
gradle test

# Run tests and generate JaCoCo XML/HTML coverage
gradle coverage

# Generate JaCoCo report explicitly
gradle jacocoTestReport

# Build artifact and run checks
gradle build

# Show available tasks
gradle tasks

# Inspect dependency tree
gradle dependencies
```

## Troubleshooting

### Build Issues

1. **Wrong Java version**: verify JDK 17+
	```bash
	java -version
	```

2. **Gradle cache/dependency problems**: refresh dependencies
	```bash
	gradle --refresh-dependencies
	```

3. **Stale build state**: clean and rebuild
	```bash
	gradle clean build
	```

### Test Issues

1. **Tests not discovered**: ensure test classes are in `src/test/kotlin` and named with `*Test`/`*Tests`
2. **JUnit 5 mismatch**: ensure `useJUnitPlatform()` remains enabled in `build.gradle.kts`

### Coverage Issues

1. **No XML report found**: run `gradle clean coverage`, then check `build/reports/jacoco/test/jacocoTestReport.xml`
2. **Stale coverage report**: use `gradle clean coverage` to force a fresh test + report generation

## Contributing

1. Follow the established Kotlin coding style and existing module patterns
2. Run `gradle test` before committing
3. Run `gradle build` to validate compilation and checks
4. Add tests for new functionality
5. Update documentation when behavior or APIs change

## Additional Resources

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [Gradle User Manual](https://docs.gradle.org/current/userguide/userguide.html)
- [JUnit 5 Documentation](https://junit.org/junit5/docs/current/user-guide/)

## License

See the main project LICENSE file for licensing information.
