package io.manycore.receiver.http.koin

import io.manycore.receiver.http.model.MimeMessage
import io.manycore.receiver.http.repository.MessageQueue

val dummyMessageQueueMock: MessageQueue =
    object : MessageQueue {

        override suspend fun enqueue(message: MimeMessage) {
            // NOOP
        }

    }

fun messageQueueMock(queue: MutableList<ByteArray>): MessageQueue =
    object : MessageQueue {

        override suspend fun enqueue(message: MimeMessage) {
            queue.add(message.asByteArray())
        }

    }
