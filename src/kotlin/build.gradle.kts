plugins {
    kotlin("jvm") version "2.1.10"
    jacoco
    `maven-publish`
}

group = "com.cyascott"
version = "1.0.0"

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.10.2")
    implementation("com.fasterxml.jackson.core:jackson-databind:2.18.2")
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin:2.18.2")

    testImplementation(kotlin("test"))
    testImplementation("org.junit.jupiter:junit-jupiter:5.11.4")
}

tasks.test {
    useJUnitPlatform()
    finalizedBy(tasks.jacocoTestReport)
}

tasks.jacocoTestReport {
    dependsOn(tasks.test)

    reports {
        xml.required.set(true)
        html.required.set(true)
        csv.required.set(false)
    }
}

tasks.register("coverage") {
    group = "verification"
    description = "Runs tests and generates JaCoCo XML/HTML coverage reports."
    dependsOn(tasks.jacocoTestReport)
}

kotlin {
    jvmToolchain(17)
}

publishing {
    publications {
        create<MavenPublication>("mavenJava") {
            from(components["java"])
            groupId = project.group.toString()
            artifactId = "poly-bus"
            version = project.version.toString()
        }
    }

    repositories {
        maven {
            val repoUrl = (findProperty("mavenRepoUrl") as String?)
                ?: System.getenv("MAVEN_REPOSITORY_URL")
                ?: ""

            if (repoUrl.isNotBlank()) {
                url = uri(repoUrl)
            }

            credentials {
                username = (findProperty("mavenUsername") as String?)
                    ?: System.getenv("MAVEN_USERNAME")
                password = (findProperty("mavenPassword") as String?)
                    ?: System.getenv("MAVEN_PASSWORD")
            }
        }
    }
}
