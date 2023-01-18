package io.manycore.receiver.http.koin

import io.manycore.receiver.http.config.Config
import io.manycore.receiver.http.repository.EventQueue
import io.manycore.receiver.http.repository.MessageQueue
import io.manycore.receiver.http.repository.RedisEventQueue
import io.manycore.receiver.http.repository.RedisMessageQueue
import org.koin.core.qualifier.named
import org.koin.dsl.module

val queuesModule = module {

    single<EventQueue> {
        val config = get<Config>()
        RedisEventQueue(config.redisHost, config.redisPort, config.eventQueueName)
    }

    single<MessageQueue>(named(Names.QUEUE_PRIORITY)) {
        val config = get<Config>()
        RedisMessageQueue(config.redisHost, config.redisPort, config.priorityQueueName)
    }

    single<MessageQueue>(named(Names.QUEUE_DEFAULT)) {
        val config = get<Config>()
        RedisMessageQueue(config.redisHost, config.redisPort, config.defaultQueueName)
    }

}

val mainModule = module {
    includes(
        queuesModule,
    )
}
