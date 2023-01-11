package io.manycore.receiver.http.platform

import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers

@Suppress("EXTENSION_SHADOWED_BY_MEMBER")
actual val IO: CoroutineDispatcher
    get() = Dispatchers.IO
