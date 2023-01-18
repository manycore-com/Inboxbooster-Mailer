package io.manycore.receiver.http.app.error

import io.ktor.http.*

/**
 * Exceptions handled in StatusPages plugin.
 */
open class HttpException(val status: HttpStatusCode, message: String? = null, cause: Throwable? = null) : Exception(
    if (message == null) status.toString() else "$status: $message", cause,
)

class BadRequestException(message: String = "Bad Request", cause: Throwable? = null) :
    HttpException(HttpStatusCode.BadRequest, message, cause)

class InternalServerError(message: String = "Internal Server Error", cause: Throwable? = null) :
    HttpException(HttpStatusCode.InternalServerError, message, cause)

class ServiceUnavailableException(message: String = "Service Unavailable", cause: Throwable? = null) :
    HttpException(HttpStatusCode.ServiceUnavailable, message, cause)
