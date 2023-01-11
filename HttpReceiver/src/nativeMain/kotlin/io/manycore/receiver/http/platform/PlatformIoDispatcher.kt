package io.manycore.receiver.http.platform

import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.newFixedThreadPoolContext

private val fixedThreadPoolDispatcher = newFixedThreadPoolContext(64, "IO")

@Suppress("EXTENSION_SHADOWED_BY_MEMBER")
actual val IO: CoroutineDispatcher
    get() = fixedThreadPoolDispatcher
