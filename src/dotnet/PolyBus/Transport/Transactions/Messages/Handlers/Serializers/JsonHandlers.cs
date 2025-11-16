using System.Text.Json;
using System.Text.Json.Nodes;

namespace PolyBus.Transport.Transactions.Messages.Handlers.Serializers;

public class JsonHandlers
{
    public JsonSerializerOptions? JsonSerializerOptions { get; set; }

    public string ContentType { get; set; } = "application/json";

    /// <summary>
    /// If the type header is missing, invalid, or if the type cannot be found, throw an exception.
    /// </summary>
    public bool ThrowOnMissingType { get; set; } = true;

    public Task Deserializer(IncomingTransaction transaction, Func<Task> next)
    {
        var message = transaction.IncomingMessage;

        var type = !message.Headers.TryGetValue(Headers.MessageType, out var header)
            ? null
            : message.Bus.Messages.GetTypeByHeader(header);

        if (type == null && ThrowOnMissingType)
        {
            throw new InvalidOperationException("The type header is missing, invalid, or if the type cannot be found.");
        }

        message.Message = type == null
            ? JsonNode.Parse(message.Body)!
            : JsonSerializer.Deserialize(message.Body, type, JsonSerializerOptions)!;

        return next();
    }

    /// <summary>
    /// If the message type is not in the list of known messages, throw an exception.
    /// </summary>
    public bool ThrowOnInvalidType { get; set; } = true;

    public Task Serializer(OutgoingTransaction transaction, Func<Task> next)
    {
        foreach (var message in transaction.OutgoingMessages)
        {
            message.Body = JsonSerializer.Serialize(message.Message, JsonSerializerOptions);
            message.Headers[Headers.ContentType] = ContentType;

            var header = message.Bus.Messages.GetHeader(message.MessageType);

            if (header != null)
            {
                message.Headers[Headers.MessageType] = header;
            }
            else if (ThrowOnInvalidType)
            {
                throw new InvalidOperationException("The header has an valid type.");
            }
        }
        return next();
    }
}
