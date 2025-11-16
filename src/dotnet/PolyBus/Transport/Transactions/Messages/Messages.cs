using System.Collections.Concurrent;
using System.Reflection;

namespace PolyBus.Transport.Transactions.Messages;

/// <summary>
/// A collection of message types and their associated message headers.
/// </summary>
public class Messages
{
    readonly ConcurrentDictionary<string, Type?> _map = new();
    readonly Dictionary<Type, (MessageInfo attribute, string header)> _types = [];

    /// <summary>
    /// Gets the message attribute associated with the specified type.
    /// </summary>
    public virtual MessageInfo? GetMessageInfo(Type type) =>
        _types.TryGetValue(type, out var value) ? value.attribute : null;

    /// <summary>
    /// Attempts to get the message type associated with the specified header.
    /// </summary>
    /// <returns>
    /// If found, returns the message type; otherwise, returns null.
    /// </returns>
    public virtual Type? GetTypeByHeader(string header)
    {
        var attribute = MessageInfo.GetAttributeFromHeader(header);
        return attribute == null ? null : _map.GetOrAdd(header, _ => _types
            .Where(pair => pair.Value.attribute.Equals(attribute))
            .Select(pair => pair.Key)
            .FirstOrDefault());
    }

    /// <summary>
    /// Attempts to get the message header associated with the specified type.
    /// </summary>
    /// <returns>
    /// If found, returns the message header; otherwise, returns null.
    /// </returns>
    public virtual string? GetHeader(Type type) =>
        _types.TryGetValue(type, out var value) ? value.header : null;

    /// <summary>
    /// Adds a message type to the collection.
    /// The message type must have a MessageAttribute defined.
    /// </summary>
    /// <returns>
    /// The MessageAttribute associated with the message type.
    /// </returns>
    /// <exception cref="ArgumentException">
    ///Type {messageType.FullName} does not have a MessageAttribute
    /// </exception>
    public virtual MessageInfo Add(Type messageType)
    {
        var attribute = messageType.GetCustomAttribute<MessageInfo>()
                        ?? throw new ArgumentException($"Type {messageType.FullName} does not have a MessageAttribute.");

        var header = attribute.ToString(true);
        _types.Add(messageType, (attribute, header));
        _map.TryAdd(header, messageType);

        return attribute;
    }

    /// <summary>
    /// Attempts to get the message type associated with the specified attribute.
    /// </summary>
    /// <returns>
    /// If found, returns the message type; otherwise, returns null.
    /// </returns>
    public virtual Type? GetTypeByMessageInfo(MessageInfo messageInfo) =>
        _types
            .Where(it => it.Value.attribute.Equals(messageInfo))
            .Select(it => it.Key)
            .FirstOrDefault();
}
