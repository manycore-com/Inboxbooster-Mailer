package io.manycore.receiver.http.app.route

import io.ktor.client.request.*
import io.ktor.http.*
import io.ktor.server.testing.*
import io.manycore.receiver.http.app.httpReceiverModule
import io.manycore.receiver.http.config.Config
import io.manycore.receiver.http.koin.Names
import io.manycore.receiver.http.koin.get
import io.manycore.receiver.http.koin.messageQueueMockModule
import io.manycore.receiver.http.koin.testModule
import io.manycore.receiver.http.platform.readResource
import org.koin.core.context.startKoin
import org.koin.core.context.stopKoin
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class MailSendRouteTest {

    @Test
    fun `Can receive basic email and push to queue`() = testApplication {

        val defaultQueue = mutableListOf<ByteArray>()

        startKoin {
            modules(
                testModule,
                messageQueueMockModule(Names.QUEUE_DEFAULT, defaultQueue),
            )
        }

        val config = get<Config>()
        val username = config.acceptedCredentials.single().first
        val password = config.acceptedCredentials.single().second

        application { httpReceiverModule() }

        val rawBasicEmail = readResource("mail/basic.eml")

        val response = client.post("/v1/mail/send") {
            basicAuth(username, password)
            contentType(ContentType.Application.OctetStream)
            setBody(rawBasicEmail)
        }

        stopKoin()

        assertEquals(HttpStatusCode.OK, response.status)
        assertEquals(1, defaultQueue.size)
        assertTrue(defaultQueue.single().contentEquals(rawBasicEmail))

    }

    @Test
    fun `Responds with 400 on invalid Content-Type`() = testApplication {

        startKoin { modules(testModule) }

        val config = get<Config>()
        val username = config.acceptedCredentials.single().first
        val password = config.acceptedCredentials.single().second

        application { httpReceiverModule() }

        val rawBasicEmail = readResource("mail/basic.eml")

        val response = client.post("/v1/mail/send") {
            basicAuth(username, password)
            contentType(ContentType.Application.Zip)
            setBody(rawBasicEmail)
        }

        stopKoin()

        assertEquals(HttpStatusCode.BadRequest, response.status)

    }

    @Test
    fun `Responds with 401 on missing authentication`() = testApplication {

        startKoin { modules(testModule) }

        application { httpReceiverModule() }

        val rawBasicEmail = readResource("mail/basic.eml")

        val response = client.post("/v1/mail/send") {
            contentType(ContentType.Application.OctetStream)
            setBody(rawBasicEmail)
        }

        stopKoin()

        assertEquals(HttpStatusCode.Unauthorized, response.status)

    }

    @Test
    fun `Responds with 401 on invalid authentication`() = testApplication {

        startKoin { modules(testModule) }

        application { httpReceiverModule() }

        val rawBasicEmail = readResource("mail/basic.eml")

        val response = client.post("/v1/mail/send") {
            basicAuth("guest", "guest")
            contentType(ContentType.Application.OctetStream)
            setBody(rawBasicEmail)
        }

        stopKoin()

        assertEquals(HttpStatusCode.Unauthorized, response.status)

    }

    @Test
    fun `Responds with 400 on invalid priority`() = testApplication {

        startKoin { modules(testModule) }

        val config = get<Config>()
        val username = config.acceptedCredentials.single().first
        val password = config.acceptedCredentials.single().second

        application { httpReceiverModule() }

        val rawInvalidPriorityEmail = readResource("mail/invalid-priority.eml")

        val response = client.post("/v1/mail/send") {
            basicAuth(username, password)
            contentType(ContentType.Application.OctetStream)
            setBody(rawInvalidPriorityEmail)
        }

        stopKoin()

        assertEquals(HttpStatusCode.BadRequest, response.status)

    }

    @Test
    fun `Responds with 400 on invalid uuid`() = testApplication {

        startKoin { modules(testModule) }

        val config = get<Config>()
        val username = config.acceptedCredentials.single().first
        val password = config.acceptedCredentials.single().second

        application { httpReceiverModule() }

        val rawInvalidUuidEmail = readResource("mail/invalid-uuid.eml")

        val response = client.post("/v1/mail/send") {
            basicAuth(username, password)
            contentType(ContentType.Application.OctetStream)
            setBody(rawInvalidUuidEmail)
        }

        stopKoin()

        assertEquals(HttpStatusCode.BadRequest, response.status)

    }

    @Test
    fun `Responds with 200 on missing priority and push to default queue`() = testApplication {

        val defaultQueue = mutableListOf<ByteArray>()
        val priorityQueue = mutableListOf<ByteArray>()

        startKoin {
            modules(
                testModule,
                messageQueueMockModule(Names.QUEUE_DEFAULT, defaultQueue),
                messageQueueMockModule(Names.QUEUE_PRIORITY, defaultQueue),
            )
        }

        val config = get<Config>()
        val username = config.acceptedCredentials.single().first
        val password = config.acceptedCredentials.single().second

        application { httpReceiverModule() }

        val rawMissingPriorityEmail = readResource("mail/missing-priority.eml")

        val response = client.post("/v1/mail/send") {
            basicAuth(username, password)
            contentType(ContentType.Application.OctetStream)
            setBody(rawMissingPriorityEmail)
        }

        stopKoin()

        assertEquals(HttpStatusCode.OK, response.status)
        assertEquals(0, priorityQueue.size)
        assertEquals(1, defaultQueue.size)
        assertTrue(defaultQueue.single().contentEquals(rawMissingPriorityEmail))

    }

    @Test
    fun `Responds with 400 on missing uuid`() = testApplication {

        startKoin { modules(testModule) }

        val config = get<Config>()
        val username = config.acceptedCredentials.single().first
        val password = config.acceptedCredentials.single().second

        application { httpReceiverModule() }

        val rawMissingUuidEmail = readResource("mail/missing-uuid.eml")

        val response = client.post("/v1/mail/send") {
            basicAuth(username, password)
            contentType(ContentType.Application.OctetStream)
            setBody(rawMissingUuidEmail)
        }

        stopKoin()

        assertEquals(HttpStatusCode.BadRequest, response.status)

    }

}
