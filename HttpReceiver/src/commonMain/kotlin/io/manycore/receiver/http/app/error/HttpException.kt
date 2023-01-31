package io.manycore.receiver.http.app.error

import io.ktor.http.*

/**
 * Exceptions handled in StatusPages plugin.
 */
open class HttpException(val status: HttpStatusCode, message: String? = null, cause: Throwable? = null) : Exception(
    if (message == null) status.toString() else "$status: $message", cause,
)

class BadRequestException(
    message: String = HttpStatusCode.BadRequest.description,
    cause: Throwable? = null,
) : HttpException(HttpStatusCode.BadRequest, message, cause)

class ForbiddenException(
    message: String = HttpStatusCode.Forbidden.description,
    cause: Throwable? = null,
) : HttpException(HttpStatusCode.Forbidden, message, cause)

class InternalServerError(
    message: String = HttpStatusCode.InternalServerError.description,
    cause: Throwable? = null,
) : HttpException(HttpStatusCode.InternalServerError, message, cause)

class ServiceUnavailableException(
    message: String = HttpStatusCode.ServiceUnavailable.description,
    cause: Throwable? = null,
) : HttpException(HttpStatusCode.ServiceUnavailable, message, cause)
