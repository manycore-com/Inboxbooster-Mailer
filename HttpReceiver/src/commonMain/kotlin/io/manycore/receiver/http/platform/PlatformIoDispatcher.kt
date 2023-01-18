package io.manycore.receiver.http.platform

import kotlinx.coroutines.CoroutineDispatcher

@Suppress("EXTENSION_SHADOWED_BY_MEMBER")
expect val IO: CoroutineDispatcher
