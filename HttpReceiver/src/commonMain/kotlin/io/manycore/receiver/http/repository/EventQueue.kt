package io.manycore.receiver.http.repository

import io.manycore.receiver.http.model.Event

interface EventQueue {

    suspend fun enqueue(event: Event)

}
