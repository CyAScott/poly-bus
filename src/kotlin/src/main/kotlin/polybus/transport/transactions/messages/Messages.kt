package polybus.transport.transactions.messages

class Messages {
    protected val types: MutableMap<Class<*>, Pair<MessageInfoValue, String>> = mutableMapOf()

    open fun getMessageInfo(type: Class<*>): MessageInfoValue {
        return types[type]?.first ?: throw PolyBusMessageNotFoundError()
    }

    open fun getHeaderByMessageInfo(messageInfo: MessageInfoValue): String {
        val contains = types.values.any { it.first.equalsInfo(messageInfo) }
        if (!contains) {
            throw PolyBusMessageNotFoundError()
        }
        return messageInfo.toHeaderString(true)
    }

    open fun add(messageType: Class<*>): MessageInfoValue {
        val annotation = messageType.getAnnotation(MessageInfo::class.java)
            ?: throw PolyBusMessageNotFoundError()
        val attribute = MessageInfoValue.fromAnnotation(annotation)
        val header = attribute.toHeaderString(true)

        if (types.containsKey(messageType)) {
            throw PolyBusMessageNotFoundError()
        }

        types[messageType] = attribute to header
        return attribute
    }

    open fun getTypeByMessageInfo(messageInfo: MessageInfoValue): Class<*> {
        return types.entries.firstOrNull { it.value.first.equalsInfo(messageInfo) }?.key
            ?: throw PolyBusMessageNotFoundError()
    }
}
