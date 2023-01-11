// TODO: Remove once KTIJ-19369 is fixed
@file:Suppress("DSL_SCOPE_VIOLATION")

import org.gradle.nativeplatform.platform.internal.DefaultNativePlatform
import org.jetbrains.kotlin.gradle.plugin.mpp.KotlinNativeTargetWithHostTestsPreset

val nativeEnabled = !project.hasProperty("disableNative")

group = "io.manycore.receiver.http"

plugins {
    alias(libs.plugins.kotlin.multiplatform)
    alias(libs.plugins.kotlinx.serialization)
}

repositories {
    mavenCentral()
}

kotlin {

    jvm {
        withJava()
    }

    if (nativeEnabled) {

        val arch = DefaultNativePlatform.getCurrentArchitecture()
        val os = DefaultNativePlatform.getCurrentOperatingSystem()
        val presetName = when {
            os.isLinux && arch.isAmd64  -> "linuxX64"
            os.isMacOsX && arch.isArm   -> "macosArm64"
            os.isMacOsX && arch.isAmd64 -> "macosX64"
            else                        -> error("Unsupported native platform: arch=$arch, os=$os")
        }
        val preset = presets.getByName(presetName) as KotlinNativeTargetWithHostTestsPreset

        targetFromPreset(preset, "native") {
            compilations.getByName("main") {
                cinterops {
                    @Suppress("UNUSED_VARIABLE")
                    val hiredis by creating
                }
            }
            binaries.executable {
                entryPoint = "${project.group}.main"
            }
        }

    }

    @Suppress("UNUSED_VARIABLE")
    sourceSets {

        val commonMain by getting {
            dependencies { implementation(libs.bundles.common) }
        }

        val commonTest by getting {
            dependencies { implementation(libs.bundles.test.common) }
        }

        val jvmMain by getting {
            dependencies { implementation(libs.bundles.jvm) }
        }

        val jvmTest by getting {
            dependencies { implementation(libs.bundles.test.jvm) }
        }

        if (nativeEnabled) {

            val nativeMain by getting {
                dependencies { implementation(libs.bundles.native) }
            }

        }

    }

}

if (nativeEnabled) {

    tasks.create("cloneHiredis") {
        doLast {
            if (!file("build/hiredis").exists()) {
                exec {
                    workingDir("build")
                    workingDir.mkdirs()
                    executable("git")
                    args(
                        "clone",
                        "-c", "advice.detachedHead=false",
                        "--depth", "1",
                        "--branch", "v${libs.versions.hiredis.get()}",
                        "https://github.com/redis/hiredis.git",
                        "--quiet",
                    )
                }
            }
        }
    }

    tasks.create("makeHiredis") {
        dependsOn("cloneHiredis")
        doLast {
            if (!file("build/hiredis/libhiredis.a").exists()) {
                exec {
                    workingDir("build/hiredis")
                    executable("make")
                    args("static")
                }
            }
        }
    }

    tasks.getByName("cinteropHiredisNative") {
        dependsOn("makeHiredis")
    }

    tasks.create("cleanHiredis") {
        doLast {
            if (file("build/hiredis").exists()) {
                exec {
                    workingDir("build/hiredis")
                    executable("make")
                    args("clean")
                }
            }
        }
    }

    tasks.getByName("clean") {
        dependsOn("cleanHiredis")
    }

}

tasks.getByName<Jar>("jvmJar") {
    doFirst {
        from(configurations.getByName("runtimeClasspath").map { if (it.isDirectory) it else zipTree(it) })
    }
    manifest.attributes["Main-Class"] = "${project.group}.MainKt"
    exclude("META-INF/*.RSA", "META-INF/*.SF", "META-INF/*.DSA")
    duplicatesStrategy = DuplicatesStrategy.INCLUDE
}

tasks.wrapper {
    gradleVersion = libs.versions.gradle.get()
}
