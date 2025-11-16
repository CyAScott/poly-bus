using System.Text.RegularExpressions;

namespace PolyBus.Transport.Transactions.Messages;

/// <summary>
/// This decorates a message class with metadata about the message.
/// This is used to identify the message type and version so that it can be routed and deserialized appropriately.
/// </summary>
/// <param name="type">If the message is a command or event.</param>
/// <param name="endpoint">The endpoint that publishes the event message or the endpoint that handles the command.</param>
/// <param name="name">The unique name for the message for the given endpoint.</param>
/// <param name="major">The major version of the message schema.</param>
/// <param name="minor">The minor version of the message schema.</param>
/// <param name="patch">The patch version of the message schema.</param>
[AttributeUsage(AttributeTargets.Class)]
public class MessageInfo(MessageType type, string endpoint, string name, int major, int minor, int patch) : Attribute
{
    /// <summary>
    /// Parses a message attribute from a message header string.
    /// </summary>
    /// <returns>
    /// If the header is valid, returns a MessageAttribute instance; otherwise, returns null.
    /// </returns>
    public static MessageInfo? GetAttributeFromHeader(string header)
    {
        var match = _headerPattern.Match(header);

        if (!match.Success)
        {
            return null;
        }

        var endpoint = match.Groups["endpoint"].Value;
        var name = match.Groups["name"].Value;
        var type = Enum.Parse<MessageType>(match.Groups["type"].Value, true);
        var major = Convert.ToInt32(match.Groups["major"].Value);
        var minor = Convert.ToInt32(match.Groups["minor"].Value);
        var patch = Convert.ToInt32(match.Groups["patch"].Value);

        return new MessageInfo(type, endpoint, name, major, minor, patch);
    }
    static readonly Regex _headerPattern = new(@"^endpoint\s*=\s*(?<endpoint>[^,\s]+),\s*type\s*=\s*(?<type>[^,\s]+),\s*name\s*=\s*(?<name>[^,\s]+),\s*version\s*=\s*(?<major>\d+)\.(?<minor>\d+)\.(?<patch>\d+)", RegexOptions.Compiled | RegexOptions.IgnoreCase);

    public MessageType Type => type;
    public int Major => major;
    public int Minor => minor;
    public int Patch => patch;
    public string Endpoint => endpoint;
    public string Name => name;

    /// <summary>
    /// Compares two message attributes for equality.
    /// The patch and minor versions are not considered for equality.
    /// </summary>
    public bool Equals(MessageInfo? other) =>
        other != null
        && Type == other.Type
        && Endpoint == other.Endpoint
        && Name == other.Name
        && Major == other.Major;
    public override bool Equals(object? obj) => obj is MessageInfo other && Equals(other);
    public override int GetHashCode() => HashCode.Combine(Type, Endpoint, Name, Major, Minor, Patch);

    /// <summary>
    /// Serializes the message attribute to a string format suitable for message headers.
    /// </summary>
    public string ToString(bool includeVersion) => $"endpoint={Endpoint}, type={type}, name={Name}" + (includeVersion ? $", version={major}.{minor}.{patch}" : "");
    public override string ToString() => ToString(true);
}
