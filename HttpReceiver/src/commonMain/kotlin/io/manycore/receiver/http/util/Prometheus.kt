package io.manycore.receiver.http.util

import kotlinx.atomicfu.AtomicLong
import kotlinx.atomicfu.atomic
import kotlinx.atomicfu.locks.SynchronizedObject
import kotlinx.atomicfu.locks.synchronized

object Prometheus {

    private val lock = SynchronizedObject()

    private val counters = mutableMapOf<CounterName, AtomicLong>()

    fun incrementCounter(name: CounterName, increment: Int = 1) = synchronized(lock) {
        require(increment > 0) { "Can't increment counter by less than 1" }
        counters.getOrPut(name) {
            atomic(0L)
        }.addAndGet(increment.toLong())
    }

    fun reset() = synchronized(lock) {
        counters.clear()
    }

    fun export(): String = buildString {
        counters
            .entries
            .sortedBy { it.key }
            .map { "${it.key.name.lowercase()}_total ${it.value.value}.0\n" }
            .forEach(::append)
    }

    enum class CounterName {
        NBR_DROPPED_EMAILS,
        NBR_EMAILS_ENQUEUED,
        NBR_RECIPIENTS,
    }

}
