package polybus.transport.transactions.messages

@Target(AnnotationTarget.CLASS)
@Retention(AnnotationRetention.RUNTIME)
annotation class MessageInfo(
    val type: MessageType,
    val endpoint: String,
    val name: String,
    val major: Int,
    val minor: Int,
    val patch: Int
)

class MessageInfoValue(
    val type: MessageType,
    val endpoint: String,
    val name: String,
    val major: Int,
    val minor: Int,
    val patch: Int
) {
    fun equalsInfo(other: MessageInfoValue?): Boolean {
        return other != null
            && type == other.type
            && endpoint == other.endpoint
            && name == other.name
            && major == other.major
    }

    override fun equals(other: Any?): Boolean = other is MessageInfoValue && equalsInfo(other)

    override fun hashCode(): Int {
        var result = type.hashCode()
        result = 31 * result + endpoint.hashCode()
        result = 31 * result + name.hashCode()
        result = 31 * result + major
        result = 31 * result + minor
        result = 31 * result + patch
        return result
    }

    fun toHeaderString(includeVersion: Boolean): String {
        val base = "endpoint=$endpoint, type=$type, name=$name"
        return if (includeVersion) "$base, version=$major.$minor.$patch" else base
    }

    override fun toString(): String = toHeaderString(true)

    companion object {
        private val _headerPattern = Regex(
            "^endpoint\\s*=\\s*(?<endpoint>[^,\\s]+),\\s*type\\s*=\\s*(?<type>[^,\\s]+),\\s*name\\s*=\\s*(?<name>[^,\\s]+),\\s*version\\s*=\\s*(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)",
            setOf(RegexOption.IGNORE_CASE)
        )

        fun getAttributeFromHeader(header: String): MessageInfoValue? {
            val match = _headerPattern.find(header) ?: return null
            val endpoint = match.groups["endpoint"]?.value ?: return null
            val name = match.groups["name"]?.value ?: return null
            val typeText = match.groups["type"]?.value ?: return null
            val type = MessageType.entries.firstOrNull { it.name.equals(typeText, ignoreCase = true) }
                ?: throw IllegalArgumentException("Requested value '$typeText' was not found.")
            val major = match.groups["major"]?.value?.toIntOrNull() ?: return null
            val minor = match.groups["minor"]?.value?.toIntOrNull() ?: return null
            val patch = match.groups["patch"]?.value?.toIntOrNull() ?: return null
            return MessageInfoValue(type, endpoint, name, major, minor, patch)
        }

        fun fromAnnotation(annotation: MessageInfo): MessageInfoValue {
            return MessageInfoValue(
                type = annotation.type,
                endpoint = annotation.endpoint,
                name = annotation.name,
                major = annotation.major,
                minor = annotation.minor,
                patch = annotation.patch
            )
        }
    }
}
