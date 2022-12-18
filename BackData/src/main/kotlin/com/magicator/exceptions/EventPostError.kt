package com.magicator.exceptions

class EventPostError : RuntimeException {
    val statusCode: Int

    constructor(message: String?, statusCode: Int) : super(message) {
        this.statusCode = statusCode
    }
}
