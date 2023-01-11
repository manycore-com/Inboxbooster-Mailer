package io.manycore.receiver.http.platform

import okio.FileSystem

@Suppress("EXTENSION_SHADOWED_BY_MEMBER")
actual val FileSystem.Companion.SYSTEM
    get() = FileSystem.SYSTEM
