package io.manycore.receiver.http.koin

import org.koin.core.component.KoinComponent
import org.koin.core.component.inject
import org.koin.core.qualifier.Qualifier
import org.koin.mp.KoinPlatformTools

inline fun <reified T : Any> get(qualifier: Qualifier? = null): T =
    object : KoinComponent {
        val value by inject<T>(qualifier)
    }.value

inline fun <reified T : Any> inject(
    qualifier: Qualifier? = null,
    mode: LazyThreadSafetyMode = KoinPlatformTools.defaultLazyMode(),
): Lazy<T> = lazy(mode) { get(qualifier) }
