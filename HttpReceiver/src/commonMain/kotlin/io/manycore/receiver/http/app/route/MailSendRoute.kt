package io.manycore.receiver.http.app.route

import io.ktor.http.*
import io.ktor.http.ContentType.Application
import io.ktor.server.application.*
import io.ktor.server.auth.*
import io.ktor.server.request.*
import io.ktor.server.resources.post
import io.ktor.server.response.*
import io.ktor.server.routing.*
import io.manycore.receiver.http.app.error.BadRequestException
import io.manycore.receiver.http.app.error.InternalServerError
import io.manycore.receiver.http.app.error.ServiceUnavailableException
import io.manycore.receiver.http.app.resource.V1MailSend
import io.manycore.receiver.http.koin.Names
import io.manycore.receiver.http.koin.inject
import io.manycore.receiver.http.model.MimeMessage
import io.manycore.receiver.http.model.MimeMessagePriority.*
import io.manycore.receiver.http.platform.IO
import io.manycore.receiver.http.platform.PlatformRedis.RedisException
import io.manycore.receiver.http.repository.MessageQueue
import kotlinx.coroutines.withContext
import org.koin.core.qualifier.named

fun Routing.setupMailSendRoute() {

    val logger = application.log

    val priorityQueue by inject<MessageQueue>(named(Names.QUEUE_PRIORITY))
    val defaultQueue by inject<MessageQueue>(named(Names.QUEUE_DEFAULT))

    authenticate {

        post<V1MailSend> {

            val requestContentType = call.request.contentType()

            if (requestContentType != Application.OctetStream) {
                throw BadRequestException("Bad Request: incorrect content type '$requestContentType', expected '${Application.OctetStream}'")
            }

            val message = try {
                withContext(IO) {
                    MimeMessage(call.receiveChannel())
                }
            } catch (t: Throwable) {
                logger.error("Failed to read mime message", t)
                throw InternalServerError(cause = t)
            }

            try {
                message.verifyHeaders()
            } catch (e: IllegalArgumentException) {
                throw BadRequestException(e.message?.let { "Bad Request: $it" } ?: "Bad Request", e)
            }

            logger.debug("Received message with priority ${message.priority} and uuid ${message.uuid}")

            val queue = when (message.priority) {
                DEFAULT -> defaultQueue
                HIGH    -> priorityQueue
            }

            withContext(IO) {
                try {
                    queue.enqueue(message)
                } catch (e: RedisException) {
                    logger.error("Failed to enqueue message with uuid ${message.uuid}", e)
                    throw ServiceUnavailableException(cause = e)
                }
            }

            call.respond(HttpStatusCode.OK)

        }

    }

}
