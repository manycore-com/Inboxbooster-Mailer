package io.manycore.receiver.http.config

data class Config(

    // App

    val appHost: String,

    val appPort: Int,

    val acceptedCredentials: List<Pair<String, String>>,

    // Queues

    val redisHost: String,

    val redisPort: Int,

    val priorityQueueName: String,

    val defaultQueueName: String,

    val eventQueueName: String,

)
