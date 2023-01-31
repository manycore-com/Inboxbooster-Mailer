package io.manycore.receiver.http.koin

import io.manycore.receiver.http.config.Config
import org.koin.core.qualifier.named
import org.koin.dsl.module

val testConfigModule = module {
    single {
        Config(
            appHost = "localhost",
            appPort = 8080,
            appMetricsPort = 9090,
            acceptedCredentials = listOf("admin" to "secret"),
            redisHost = "localhost",
            redisPort = 6379,
            priorityQueueName = "priority-queue",
            defaultQueueName = "default-queue",
            eventQueueName = "event-queue",
        )
    }
}

val dummyQueuesModule = module {
    single(named(Names.QUEUE_DEFAULT)) { dummyMessageQueueMock }
    single(named(Names.QUEUE_PRIORITY)) { dummyMessageQueueMock }
}

val testModule = module {
    includes(
        mainModule,
        testConfigModule,
        dummyQueuesModule,
    )
}

fun messageQueueMockModule(
    name: String,
    queue: MutableList<ByteArray>,
) = module {
    single(named(name)) {
        messageQueueMock(queue)
    }
}
