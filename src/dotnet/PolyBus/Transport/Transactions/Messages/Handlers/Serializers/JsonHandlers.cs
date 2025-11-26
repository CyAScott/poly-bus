using System.Text.Json;

namespace PolyBus.Transport.Transactions.Messages.Handlers.Serializers;

/// <summary>
/// Handlers for serializing and deserializing messages as JSON.
/// </summary>
public class JsonHandlers
{
    /// <summary>
    /// The options to use for the JSON serializer.
    /// </summary>
    public JsonSerializerOptions? JsonSerializerOptions { get; set; }

    /// <summary>
    /// The content type to set on outgoing messages.
    /// </summary>
    public string ContentType { get; set; } = "application/json";

    /// <summary>
    /// The header key to use for the content type.
    /// </summary>
    public string Header { get; set; } = Headers.ContentType;

    /// <summary>
    /// Deserializes incoming messages from JSON.
    /// </summary>
    public virtual Task Deserializer(IncomingTransaction transaction, Func<Task> next)
    {
        var incomingMessage = transaction.IncomingMessage;

        incomingMessage.Message = JsonSerializer.Deserialize(incomingMessage.Body, incomingMessage.MessageType, JsonSerializerOptions)!;

        return next();
    }

    /// <summary>
    /// Serializes outgoing messages to JSON.
    /// </summary>
    public virtual Task Serializer(OutgoingTransaction transaction, Func<Task> next)
    {
        foreach (var message in transaction.OutgoingMessages)
        {
            message.Body = JsonSerializer.Serialize(message.Message, JsonSerializerOptions);
            message.Headers[Header] = ContentType;
        }
        return next();
    }
}
