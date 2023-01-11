package io.manycore.receiver.http.app.resource

import io.ktor.resources.*
import kotlinx.serialization.Serializable

@Resource("/v1/mail/send")
@Serializable
object V1MailSend
