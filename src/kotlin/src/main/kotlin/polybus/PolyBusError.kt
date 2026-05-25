package polybus

open class PolyBusError(val errorCode: Int, message: String) : RuntimeException(message)
