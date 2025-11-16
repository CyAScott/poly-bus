using System.Text.Json;
using System.Text.Json.Nodes;
using NUnit.Framework;

namespace PolyBus.Transport.Transactions.Messages.Handlers.Serializers;

[TestFixture]
public class JsonHandlersTests
{
    private JsonHandlers _jsonHandlers = null!;
    private IPolyBus _mockBus = null!;
    private Messages _messages = null!;

    [SetUp]
    public void SetUp()
    {
        _jsonHandlers = new JsonHandlers();
        _messages = new Messages();
        _mockBus = new MockPolyBus(_messages);
    }

    #region Deserializer Tests

    [Test]
    public async Task Deserializer_WithValidTypeHeader_DeserializesMessage()
    {
        // Arrange
        var testMessage = new TestMessage { Id = 1, Name = "Test" };
        var serializedBody = JsonSerializer.Serialize(testMessage);

        _messages.Add(typeof(TestMessage));

        var incomingMessage = new IncomingMessage(_mockBus, serializedBody)
        {
            Headers = new Dictionary<string, string>
            {
                [Headers.MessageType] = _header
            }
        };
        var transaction = new MockIncomingTransaction(_mockBus, incomingMessage);

        var nextCalled = false;
        Task Next() { nextCalled = true; return Task.CompletedTask; }

        // Act
        await _jsonHandlers.Deserializer(transaction, Next);

        // Assert
        Assert.That(nextCalled, Is.True);
        Assert.That(incomingMessage.Message, Is.Not.Null);
        Assert.That(incomingMessage.Message, Is.TypeOf<TestMessage>());
        var deserializedMessage = (TestMessage)incomingMessage.Message;
        Assert.That(deserializedMessage.Id, Is.EqualTo(1));
        Assert.That(deserializedMessage.Name, Is.EqualTo("Test"));
    }

    [Test]
    public async Task Deserializer_WithValidTypeHeaderAndCustomOptions_DeserializesWithOptions()
    {
        // Arrange
        var options = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        };
        var jsonHandlers = new JsonHandlers { JsonSerializerOptions = options };

        var testMessage = new TestMessage { Id = 2, Name = "CamelCase" };
        var serializedBody = JsonSerializer.Serialize(testMessage, options);

        _messages.Add(typeof(TestMessage));

        var incomingMessage = new IncomingMessage(_mockBus, serializedBody)
        {
            Headers = new Dictionary<string, string>
            {
                [Headers.MessageType] = _header
            }
        };
        var transaction = new MockIncomingTransaction(_mockBus, incomingMessage);

        var nextCalled = false;
        Task Next() { nextCalled = true; return Task.CompletedTask; }

        // Act
        await jsonHandlers.Deserializer(transaction, Next);

        // Assert
        Assert.That(nextCalled, Is.True);
        Assert.That(incomingMessage.Message, Is.TypeOf<TestMessage>());
        var deserializedMessage = (TestMessage)incomingMessage.Message;
        Assert.That(deserializedMessage.Id, Is.EqualTo(2));
        Assert.That(deserializedMessage.Name, Is.EqualTo("CamelCase"));
    }

    [Test]
    public async Task Deserializer_WithUnknownTypeAndThrowOnMissingTypeFalse_ParsesAsJsonNode()
    {
        // Arrange
        var jsonHandlers = new JsonHandlers { ThrowOnMissingType = false };
        var testObject = new { Id = 3, Name = "Unknown" };
        var serializedBody = JsonSerializer.Serialize(testObject);
        var header = "endpoint=test-service, type=Command, name=UnknownMessage, version=1.0.0";

        var incomingMessage = new IncomingMessage(_mockBus, serializedBody)
        {
            Headers = new Dictionary<string, string>
            {
                [Headers.MessageType] = header
            }
        };
        var transaction = new MockIncomingTransaction(_mockBus, incomingMessage);

        var nextCalled = false;
        Task Next() { nextCalled = true; return Task.CompletedTask; }

        // Act
        await jsonHandlers.Deserializer(transaction, Next);

        // Assert
        Assert.That(nextCalled, Is.True);
        Assert.That(incomingMessage.Message, Is.Not.Null);
        Assert.That(incomingMessage.Message, Is.InstanceOf<JsonNode>());
        var jsonNode = (JsonNode)incomingMessage.Message;
        Assert.That(jsonNode["Id"]?.GetValue<int>(), Is.EqualTo(3));
        Assert.That(jsonNode["Name"]?.GetValue<string>(), Is.EqualTo("Unknown"));
    }

    [Test]
    public void Deserializer_WithUnknownTypeAndThrowOnMissingTypeTrue_ThrowsException()
    {
        // Arrange
        var jsonHandlers = new JsonHandlers { ThrowOnMissingType = true };
        var testObject = new { Id = 4, Name = "Error" };
        var serializedBody = JsonSerializer.Serialize(testObject);
        var header = "endpoint=test-service, type=Command, name=UnknownMessage, version=1.0.0";

        var incomingMessage = new IncomingMessage(_mockBus, serializedBody)
        {
            Headers = new Dictionary<string, string>
            {
                [Headers.MessageType] = header
            }
        };
        var transaction = new MockIncomingTransaction(_mockBus, incomingMessage);

        Task Next() => Task.CompletedTask;

        // Act & Assert
        var ex = Assert.ThrowsAsync<InvalidOperationException>(
            () => jsonHandlers.Deserializer(transaction, Next));
        Assert.That(ex!.Message, Is.EqualTo("The type header is missing, invalid, or if the type cannot be found."));
    }

    [Test]
    public void Deserializer_WithMissingTypeHeader_SkipsDeserialization()
    {
        // Arrange
        var jsonHandlers = new JsonHandlers { ThrowOnMissingType = true };
        var incomingMessage = new IncomingMessage(_mockBus, "{}")
        {
            Headers = new Dictionary<string, string>()
        };
        var transaction = new MockIncomingTransaction(_mockBus, incomingMessage);

        Task Next() => Task.CompletedTask;

        // Act & Assert
        var ex = Assert.ThrowsAsync<InvalidOperationException>(
            () => jsonHandlers.Deserializer(transaction, Next));
        Assert.That(ex!.Message, Is.EqualTo("The type header is missing, invalid, or if the type cannot be found."));
    }

    [Test]
    public void Deserializer_WithInvalidJson_ThrowsJsonException()
    {
        // Arrange
        _messages.Add(typeof(TestMessage));

        var incomingMessage = new IncomingMessage(_mockBus, "invalid json")
        {
            Headers = new Dictionary<string, string>
            {
                [Headers.MessageType] = _header
            }
        };
        var transaction = new MockIncomingTransaction(_mockBus, incomingMessage);

        Task Next() => Task.CompletedTask;

        // Act & Assert
        Assert.ThrowsAsync<JsonException>(() => _jsonHandlers.Deserializer(transaction, Next));
    }

    #endregion

    #region Serializer Tests

    [Test]
    public async Task Serializer_WithValidMessage_SerializesAndSetsHeaders()
    {
        // Arrange
        var testMessage = new TestMessage { Id = 5, Name = "Serialize" };
        var messageType = typeof(TestMessage);
        var expectedHeader = _header;

        _messages.Add(messageType);

        var mockTransaction = new MockOutgoingTransaction(_mockBus);
        var outgoingMessage = mockTransaction.AddOutgoingMessage(testMessage);

        var nextCalled = false;
        Task Next() { nextCalled = true; return Task.CompletedTask; }

        // Act
        await _jsonHandlers.Serializer(mockTransaction, Next);

        // Assert
        Assert.That(nextCalled, Is.True);
        Assert.That(outgoingMessage.Body, Is.Not.Null);

        var deserializedMessage = JsonSerializer.Deserialize<TestMessage>(outgoingMessage.Body);
        Assert.That(deserializedMessage!.Id, Is.EqualTo(5));
        Assert.That(deserializedMessage.Name, Is.EqualTo("Serialize"));

        Assert.That(outgoingMessage.Headers[Headers.ContentType], Is.EqualTo("application/json"));
        Assert.That(outgoingMessage.Headers[Headers.MessageType], Is.EqualTo(expectedHeader));
    }

    [Test]
    public async Task Serializer_WithCustomContentType_UsesCustomContentType()
    {
        // Arrange
        var customContentType = "application/custom-json";
        var jsonHandlers = new JsonHandlers { ContentType = customContentType, ThrowOnInvalidType = false };

        var testMessage = new TestMessage { Id = 6, Name = "Custom" };
        _messages.Add(typeof(TestMessage));

        var mockTransaction = new MockOutgoingTransaction(_mockBus);
        var outgoingMessage = mockTransaction.AddOutgoingMessage(testMessage);

        var nextCalled = false;
        Task Next() { nextCalled = true; return Task.CompletedTask; }

        // Act
        await jsonHandlers.Serializer(mockTransaction, Next);

        // Assert
        Assert.That(nextCalled, Is.True);
        Assert.That(outgoingMessage.Headers[Headers.ContentType], Is.EqualTo(customContentType));
    }

    [Test]
    public async Task Serializer_WithCustomJsonOptions_SerializesWithOptions()
    {
        // Arrange
        var options = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        };
        var jsonHandlers = new JsonHandlers { JsonSerializerOptions = options, ThrowOnInvalidType = false };

        var testMessage = new TestMessage { Id = 7, Name = "Options" };
        _messages.Add(typeof(TestMessage));

        var mockTransaction = new MockOutgoingTransaction(_mockBus);
        var outgoingMessage = mockTransaction.AddOutgoingMessage(testMessage);

        var nextCalled = false;
        Task Next() { nextCalled = true; return Task.CompletedTask; }

        // Act
        await jsonHandlers.Serializer(mockTransaction, Next);

        // Assert
        Assert.That(nextCalled, Is.True);
        Assert.That(outgoingMessage.Body, Contains.Substring("\"id\":"));
        Assert.That(outgoingMessage.Body, Contains.Substring("\"name\":"));
    }

    [Test]
    public async Task Serializer_WithUnknownTypeAndThrowOnInvalidTypeFalse_SkipsHeaderSetting()
    {
        // Arrange
        var jsonHandlers = new JsonHandlers { ThrowOnInvalidType = false };

        var testMessage = new UnknownMessage { Data = "test" };

        var mockTransaction = new MockOutgoingTransaction(_mockBus);
        var outgoingMessage = mockTransaction.AddOutgoingMessage(testMessage, "unknown-endpoint");

        var nextCalled = false;
        Task Next() { nextCalled = true; return Task.CompletedTask; }

        // Act
        await jsonHandlers.Serializer(mockTransaction, Next);

        // Assert
        Assert.That(nextCalled, Is.True);
        Assert.That(outgoingMessage.Body, Is.Not.Null);
        Assert.That(outgoingMessage.Headers[Headers.ContentType], Is.EqualTo("application/json"));
        Assert.That(outgoingMessage.Headers.ContainsKey(Headers.MessageType), Is.False);
    }

    [Test]
    public void Serializer_WithUnknownTypeAndThrowOnInvalidTypeTrue_ThrowsException()
    {
        // Arrange
        var jsonHandlers = new JsonHandlers { ThrowOnInvalidType = true };

        var testMessage = new UnknownMessage { Data = "error" };

        var mockTransaction = new MockOutgoingTransaction(_mockBus);
        mockTransaction.AddOutgoingMessage(testMessage, "unknown-endpoint");

        Task Next() => Task.CompletedTask;

        // Act & Assert
        var ex = Assert.ThrowsAsync<InvalidOperationException>(
            () => jsonHandlers.Serializer(mockTransaction, Next));
        Assert.That(ex!.Message, Is.EqualTo("The header has an valid type."));
    }

    [Test]
    public async Task Serializer_WithMultipleMessages_SerializesAll()
    {
        // Arrange
        var testMessage1 = new TestMessage { Id = 8, Name = "First" };
        var testMessage2 = new TestMessage { Id = 9, Name = "Second" };

        _messages.Add(typeof(TestMessage));

        var mockTransaction = new MockOutgoingTransaction(_mockBus);
        var outgoingMessage1 = mockTransaction.AddOutgoingMessage(testMessage1);
        outgoingMessage1.Headers[Headers.MessageType] = _header;
        var outgoingMessage2 = mockTransaction.AddOutgoingMessage(testMessage2);
        outgoingMessage2.Headers[Headers.MessageType] = _header;

        var nextCalled = false;
        Task Next() { nextCalled = true; return Task.CompletedTask; }

        // Act
        await _jsonHandlers.Serializer(mockTransaction, Next);

        // Assert
        Assert.That(nextCalled, Is.True);
        Assert.That(outgoingMessage1.Body, Is.Not.Null);
        Assert.That(outgoingMessage2.Body, Is.Not.Null);

        var deserializedMessage1 = JsonSerializer.Deserialize<TestMessage>(outgoingMessage1.Body);
        var deserializedMessage2 = JsonSerializer.Deserialize<TestMessage>(outgoingMessage2.Body);

        Assert.That(deserializedMessage1!.Id, Is.EqualTo(8));
        Assert.That(deserializedMessage1.Name, Is.EqualTo("First"));
        Assert.That(deserializedMessage2!.Id, Is.EqualTo(9));
        Assert.That(deserializedMessage2.Name, Is.EqualTo("Second"));
    }

    [Test]
    public async Task Serializer_WithEmptyOutgoingMessages_CallsNext()
    {
        // Arrange
        var mockTransaction = new MockOutgoingTransaction(_mockBus);

        var nextCalled = false;
        Task Next() { nextCalled = true; return Task.CompletedTask; }

        // Act
        await _jsonHandlers.Serializer(mockTransaction, Next);

        // Assert
        Assert.That(nextCalled, Is.True);
    }

    #endregion

    #region Test Support Classes

    const string _header = "endpoint=test-service, type=Command, name=TestMessage, version=1.0.0";
    [MessageInfo(MessageType.Command, "test-service", "TestMessage", 1, 0, 0)]
    public class TestMessage
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
    }

    public class UnknownMessage
    {
        public string Data { get; set; } = string.Empty;
    }

    #endregion

    private class MockPolyBus(Messages messages) : IPolyBus
    {
        public IDictionary<string, object> Properties => null!;
        public ITransport Transport => null!;
        public IList<IncomingHandler> IncomingHandlers => [];
        public IList<OutgoingHandler> OutgoingHandlers => [];
        public Messages Messages { get; } = messages;
        public string Name => "MockBus";

        public Task<Transaction> CreateTransaction(IncomingMessage? message = null) =>
            Task.FromResult<Transaction>(
                message != null
                ? new MockIncomingTransaction(this, message)
                : new MockOutgoingTransaction(this));

        public Task Send(Transaction transaction) => Task.CompletedTask;
        public Task Start() => Task.CompletedTask;
        public Task Stop() => Task.CompletedTask;
    }

    private class MockOutgoingTransaction(IPolyBus bus) : OutgoingTransaction(bus)
    {
        public override Task Abort() => Task.CompletedTask;
        public override Task Commit() => Task.CompletedTask;
    }

    private class MockIncomingTransaction(IPolyBus bus, IncomingMessage incomingMessage) : IncomingTransaction(bus, incomingMessage)
    {
        public override Task Abort() => Task.CompletedTask;
        public override Task Commit() => Task.CompletedTask;
    }
}
