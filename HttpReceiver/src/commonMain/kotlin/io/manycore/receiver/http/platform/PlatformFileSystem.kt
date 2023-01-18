package io.manycore.receiver.http.platform

import okio.FileSystem

@Suppress("EXTENSION_SHADOWED_BY_MEMBER")
expect val FileSystem.Companion.SYSTEM: FileSystem
