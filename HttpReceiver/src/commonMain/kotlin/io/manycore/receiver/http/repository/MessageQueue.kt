package io.manycore.receiver.http.repository

import io.manycore.receiver.http.model.MimeMessage

interface MessageQueue {

    suspend fun enqueue(message: MimeMessage)

}
