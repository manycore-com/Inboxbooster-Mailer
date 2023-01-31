package io.manycore.receiver.http.config

import io.ktor.util.logging.*
import io.manycore.receiver.http.platform.SYSTEM
import io.manycore.receiver.http.platform.exitProcess
import net.mamoe.yamlkt.Yaml
import net.mamoe.yamlkt.YamlElement
import net.mamoe.yamlkt.YamlList
import net.mamoe.yamlkt.YamlLiteral
import net.mamoe.yamlkt.YamlMap
import net.mamoe.yamlkt.literalContentOrNull
import okio.FileNotFoundException
import okio.FileSystem
import okio.Path.Companion.toPath
import okio.buffer

object MainConfigLoader {

    private const val ARG_GLOBAL_CONFIG = "--global-config-file"

    private const val ARG_CUSTOMER_CONFIG = "--customer-config-file"

    private val log = KtorSimpleLogger("MainConfigLoader")

    fun loadConfig(args: Array<String>): Config {
        val globalConfigFile = args.getArgument(ARG_GLOBAL_CONFIG)
        val customerConfigFile = args.getArgument(ARG_CUSTOMER_CONFIG)

        val globalConfigContent = readFile(globalConfigFile)
        val customerConfigContent = readFile(customerConfigFile)

        return loadConfig(globalConfigContent, customerConfigContent)
    }

    fun loadConfig(globalConfigContent: String, customerConfigContent: String): Config {
        val globalConfig = Yaml.decodeYamlMapFromString(globalConfigContent)
        val customerConfig = Yaml.decodeYamlMapFromString(customerConfigContent)
        return loadConfig(globalConfig, customerConfig)
    }

    fun loadConfig(globalConfig: YamlMap, customerConfig: YamlMap): Config =
        Config(
            appHost = customerConfig.getPathAsStringOrFail("httpreceiver.bind.inet-interface"),
            appPort = customerConfig.getPathAsIntOrFail("httpreceiver.bind.inet-port"),
            appMetricsPort = customerConfig.getPathAsIntOrFail("httpreceiver.bind.inet-port-metrics"),
            acceptedCredentials = readAcceptedCredentials(customerConfig),
            redisHost = customerConfig.getPathAsStringOrFail("httpreceiver.reliable-queue.redis.hostname"),
            redisPort = customerConfig.getPathAsIntOrFail("httpreceiver.reliable-queue.redis.port"),
            priorityQueueName = globalConfig.getPathAsStringOrFail("reliable-queue.queue-names.primary-queue"),
            defaultQueueName = globalConfig.getPathAsStringOrFail("reliable-queue.queue-names.default-queue"),
            eventQueueName = globalConfig.getPathAsStringOrFail("backdata.queue-name"),
        )

    private fun Array<String>.getArgument(key: String): String {
        val keyIndex = indexOf(key)
        val valueIndex = keyIndex + 1
        if (keyIndex == -1 || valueIndex !in indices) {
            log.error("Missing argument $key")
            exitProcess(1)
        } else {
            return get(valueIndex)
        }
    }

    private fun readFile(file: String): String {
        val path = file.toPath()
        val source = try {
            FileSystem.SYSTEM.source(path)
        } catch (e: FileNotFoundException) {
            log.error("File not found: $path")
            exitProcess(1)
        }
        val bufferedSource = source.buffer()
        val content = try {
            bufferedSource.readUtf8()
        } finally {
            bufferedSource.close()
            source.close()
        }
        return content
    }

    private tailrec fun YamlMap.getPath(path: String): YamlElement? =
        if ('.' !in path) {
            get(path)
        } else {
            val map = get(path.substringBefore('.')) as? YamlMap
            map?.getPath(path.substringAfter('.'))
        }

    private fun YamlMap.getPathAsStringOrFail(path: String): String =
        getPath(path)?.literalContentOrNull ?: failWithInvalidConfigField(path)

    private fun YamlMap.getPathAsIntOrFail(path: String): Int =
        getPathAsStringOrFail(path).toInt()

    private fun failWithInvalidConfigField(
        field: String,
        configName: String = "customer",
        cause: String = "is missing",
    ): Nothing {
        log.error("Error in $configName configuration: '$field' $cause")
        exitProcess(1)
    }

    private fun readAcceptedCredentials(customerConfig: YamlMap): List<Pair<String, String>> {
        val authLogins = customerConfig.getPath("httpreceiver.auth-logins")
            ?: failWithInvalidConfigField("httpreceiver.auth-logins")
        if (authLogins !is YamlList || authLogins.any { it !is YamlMap }) {
            failWithInvalidConfigField("httpreceiver.auth-logins", cause = "should be a list of objects")
        }
        return authLogins.map {
            val element = it as YamlMap
            val username = element["username"]
            if (username == null || username !is YamlLiteral) {
                failWithInvalidConfigField(
                    "httpreceiver.auth-logins",
                    cause = "objects should contain field 'username'"
                )
            }
            val password = element["password"]
            if (password == null || password !is YamlLiteral) {
                failWithInvalidConfigField(
                    "httpreceiver.auth-logins",
                    cause = "objects should contain field 'password'"
                )
            }
            return@map username.content to password.content
        }
    }

}
