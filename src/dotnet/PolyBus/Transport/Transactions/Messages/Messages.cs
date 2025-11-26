using System.Reflection;

namespace PolyBus.Transport.Transactions.Messages;

/// <summary>
/// A collection of message types and their associated message headers and attributes.
/// </summary>
public class Messages
{
    protected Dictionary<Type, (MessageInfo attribute, string header)> Types { get; } = [];

    /// <summary>
    /// Gets the message attribute associated with the specified type.
    /// </summary>
    /// <returns>
    /// The MessageInfoAttribute associated with the specified type.
    /// </returns>
    /// <exception cref="PolyBusMessageNotFoundError">
    /// If no message attribute is found for the specified type.
    /// </exception>
    public virtual MessageInfo GetMessageInfo(Type type) =>
        Types.TryGetValue(type, out var value)
            ? value.attribute
            : throw new PolyBusMessageNotFoundError();

    /// <summary>
    /// Gets the message header associated with the specified attribute.
    /// </summary>
    /// <returns>
    /// The message header associated with the specified attribute.
    /// </returns>
    /// <exception cref="PolyBusMessageNotFoundError">
    /// If no message header is found for the specified attribute.
    /// </exception>
    public virtual string GetHeaderByMessageInfo(MessageInfo messageInfo) =>
        Types.Values.Any(it => it.attribute.Equals(messageInfo))
            ? messageInfo.ToString(true)
            : throw new PolyBusMessageNotFoundError();

    /// <summary>
    /// Adds a message type to the collection.
    /// The message type must have a MessageAttribute defined.
    /// </summary>
    /// <returns>
    /// The MessageAttribute associated with the message type.
    /// </returns>
    /// <exception cref="PolyBusMessageNotFoundError">
    /// If the message type does not have a message info attribute defined.
    /// </exception>
    public virtual MessageInfo Add(Type messageType)
    {
        var attribute = messageType.GetCustomAttribute<MessageInfo>()
                                   ?? throw new PolyBusMessageNotFoundError();

        var header = attribute.ToString(true);

        if (!Types.TryAdd(messageType, (attribute, header)))
        {
            throw new PolyBusMessageNotFoundError();
        }

        return attribute;
    }

    /// <summary>
    /// Attempts to get the message type associated with the specified attribute.
    /// </summary>
    /// <returns>
    /// The message type associated with the specified attribute.
    /// </returns>
    /// <exception cref="PolyBusMessageNotFoundError">
    /// If no message type is found for the specified message info attribute.
    /// </exception>
    public virtual Type GetTypeByMessageInfo(MessageInfo messageInfo) =>
        Types
            .Where(it => it.Value.attribute.Equals(messageInfo))
            .Select(it => it.Key)
            .FirstOrDefault()
        ?? throw new PolyBusMessageNotFoundError();
}
