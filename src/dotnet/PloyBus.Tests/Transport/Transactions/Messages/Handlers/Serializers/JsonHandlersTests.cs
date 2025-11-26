using NUnit.Framework;

namespace PolyBus.Transport.Transactions.Messages.Handlers.Serializers;

[TestFixture]
public class JsonHandlersTests
{
    private JsonHandlers _jsonHandlers = null!;
    private Messages _messages = null!;

    [SetUp]
    public void SetUp()
    {
        _jsonHandlers = new JsonHandlers();
        _messages = new();
        _messages.Add(typeof(JsonHandlerTestMessage));
    }

    public async Task Serializer_SetsBodyAndContentType()
    {
        // Arrange
        var message = new JsonHandlerTestMessage { Text = "Hello, World!" };
        var outgoingMessage = new OutgoingMessage(null!, message)
        {
            Message = message,
            MessageType = typeof(JsonHandlerTestMessage)
        };
        var transaction = new OutgoingTransaction(null!);
        transaction.Add(message);

        // Act
        await _jsonHandlers.Serializer(transaction, () => Task.CompletedTask);

        // Assert
        Assert.That(outgoingMessage.Body, Is.Not.Null);
        Assert.That(outgoingMessage.Headers[Headers.ContentType], Is.EqualTo("application/json"));
    }
}
