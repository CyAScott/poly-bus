using NUnit.Framework;

namespace PolyBus.Transport.Transactions.Messages;

[TestFixture]
public class MessagesTests
{
    private Messages _messages = null!;

    [SetUp]
    public void SetUp()
    {
        _messages = new Messages();
    }

    #region Test Message Classes

    [MessageInfo(MessageType.Command, "OrderService", "CreateOrder", 1, 0, 0)]
    public class CreateOrderCommand
    {
        public string OrderId { get; set; } = string.Empty;
        public decimal Amount { get; set; }
    }

    [MessageInfo(MessageType.Event, "OrderService", "OrderCreated", 2, 1, 3)]
    public class OrderCreatedEvent
    {
        public string OrderId { get; set; } = string.Empty;
        public DateTime CreatedAt { get; set; }
    }

    [MessageInfo(MessageType.Command, "PaymentService", "ProcessPayment", 1, 5, 2)]
    public class ProcessPaymentCommand
    {
        public string PaymentId { get; set; } = string.Empty;
        public decimal Amount { get; set; }
    }

    public class MessageWithoutAttribute
    {
        public string Data { get; set; } = string.Empty;
    }

    #endregion

    [Test]
    public void Add_ValidMessageType_ReturnsMessageInfo()
    {
        // Act
        var result = _messages.Add(typeof(CreateOrderCommand));

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result.Type, Is.EqualTo(MessageType.Command));
        Assert.That(result.Endpoint, Is.EqualTo("OrderService"));
        Assert.That(result.Name, Is.EqualTo("CreateOrder"));
        Assert.That(result.Major, Is.EqualTo(1));
        Assert.That(result.Minor, Is.EqualTo(0));
        Assert.That(result.Patch, Is.EqualTo(0));
    }

    [Test]
    public void Add_MessageTypeWithoutAttribute_ThrowsArgumentException()
    {
        // Act & Assert
        var exception = Assert.Throws<ArgumentException>(() => _messages.Add(typeof(MessageWithoutAttribute)));
        Assert.That(exception.Message, Does.Contain("does not have a MessageAttribute"));
        Assert.That(exception.Message, Does.Contain(typeof(MessageWithoutAttribute).FullName));
    }

    [Test]
    public void GetMessageInfo_ExistingType_ReturnsCorrectMessageInfo()
    {
        // Arrange
        _messages.Add(typeof(CreateOrderCommand));

        // Act
        var result = _messages.GetMessageInfo(typeof(CreateOrderCommand));

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result.Type, Is.EqualTo(MessageType.Command));
        Assert.That(result.Endpoint, Is.EqualTo("OrderService"));
        Assert.That(result.Name, Is.EqualTo("CreateOrder"));
    }

    [Test]
    public void GetMessageInfo_NonExistentType_ReturnsNull()
    {
        // Act
        var result = _messages.GetMessageInfo(typeof(CreateOrderCommand));

        // Assert
        Assert.That(result, Is.Null);
    }

    [Test]
    public void GetHeader_ExistingType_ReturnsCorrectHeader()
    {
        // Arrange
        _messages.Add(typeof(OrderCreatedEvent));

        // Act
        var result = _messages.GetHeader(typeof(OrderCreatedEvent));

        // Assert
        Assert.That(result, Is.EqualTo("endpoint=OrderService, type=Event, name=OrderCreated, version=2.1.3"));
    }

    [Test]
    public void GetHeader_NonExistentType_ReturnsNull()
    {
        // Act
        var result = _messages.GetHeader(typeof(CreateOrderCommand));

        // Assert
        Assert.That(result, Is.Null);
    }

    [Test]
    public void GetTypeByHeader_ValidHeader_ReturnsCorrectType()
    {
        // Arrange
        _messages.Add(typeof(ProcessPaymentCommand));
        var header = "endpoint=PaymentService, type=Command, name=ProcessPayment, version=1.5.2";

        // Act
        var result = _messages.GetTypeByHeader(header);

        // Assert
        Assert.That(result, Is.EqualTo(typeof(ProcessPaymentCommand)));
    }

    [Test]
    public void GetTypeByHeader_InvalidHeader_ReturnsNull()
    {
        // Arrange
        const string InvalidHeader = "invalid header format";

        // Act
        var result = _messages.GetTypeByHeader(InvalidHeader);

        // Assert
        Assert.That(result, Is.Null);
    }

    [Test]
    public void GetTypeByHeader_NonExistentMessage_ReturnsNull()
    {
        // Arrange
        const string Header = "endpoint=UnknownService, type=Command, name=UnknownCommand, version=1.0.0";

        // Act
        var result = _messages.GetTypeByHeader(Header);

        // Assert
        Assert.That(result, Is.Null);
    }

    [Test]
    public void GetTypeByHeader_CachesResults()
    {
        // Arrange
        _messages.Add(typeof(CreateOrderCommand));
        const string Header = "endpoint=OrderService, type=Command, name=CreateOrder, version=1.0.0";

        // Act
        var result1 = _messages.GetTypeByHeader(Header);
        var result2 = _messages.GetTypeByHeader(Header);

        // Assert
        Assert.That(result1, Is.EqualTo(typeof(CreateOrderCommand)));
        Assert.That(result2, Is.EqualTo(typeof(CreateOrderCommand)));
        Assert.That(ReferenceEquals(result1, result2), Is.True);
    }

    [Test]
    public void GetTypeByMessageInfo_ExistingMessageInfo_ReturnsCorrectType()
    {
        // Arrange
        _messages.Add(typeof(OrderCreatedEvent));
        var messageInfo = new MessageInfo(MessageType.Event, "OrderService", "OrderCreated", 2, 1, 3);

        // Act
        var result = _messages.GetTypeByMessageInfo(messageInfo);

        // Assert
        Assert.That(result, Is.EqualTo(typeof(OrderCreatedEvent)));
    }

    [Test]
    public void GetTypeByMessageInfo_NonExistentMessageInfo_ReturnsNull()
    {
        // Arrange
        var messageInfo = new MessageInfo(MessageType.Command, "UnknownService", "UnknownCommand", 1, 0, 0);

        // Act
        var result = _messages.GetTypeByMessageInfo(messageInfo);

        // Assert
        Assert.That(result, Is.Null);
    }

    [Test]
    public void GetTypeByMessageInfo_DifferentMinorPatchVersions_ReturnsType()
    {
        // Arrange
        _messages.Add(typeof(OrderCreatedEvent)); // Has version 2.1.3
        var messageInfoDifferentMinor = new MessageInfo(MessageType.Event, "OrderService", "OrderCreated", 2, 5, 3);
        var messageInfoDifferentPatch = new MessageInfo(MessageType.Event, "OrderService", "OrderCreated", 2, 1, 9);

        // Act
        var result1 = _messages.GetTypeByMessageInfo(messageInfoDifferentMinor);
        var result2 = _messages.GetTypeByMessageInfo(messageInfoDifferentPatch);

        // Assert
        Assert.That(result1, Is.EqualTo(typeof(OrderCreatedEvent)));
        Assert.That(result2, Is.EqualTo(typeof(OrderCreatedEvent)));
    }

    [Test]
    public void GetTypeByMessageInfo_DifferentMajorVersion_ReturnsNull()
    {
        // Arrange
        _messages.Add(typeof(OrderCreatedEvent)); // Has version 2.1.3
        var messageInfoDifferentMajor = new MessageInfo(MessageType.Event, "OrderService", "OrderCreated", 3, 1, 3);

        // Act
        var result = _messages.GetTypeByMessageInfo(messageInfoDifferentMajor);

        // Assert
        Assert.That(result, Is.Null);
    }

    [Test]
    public void MultipleMessages_AllMethodsWorkCorrectly()
    {
        // Arrange
        _messages.Add(typeof(CreateOrderCommand));
        _messages.Add(typeof(OrderCreatedEvent));
        _messages.Add(typeof(ProcessPaymentCommand));

        // Act & Assert - GetMessageInfo
        var commandInfo = _messages.GetMessageInfo(typeof(CreateOrderCommand));
        var eventInfo = _messages.GetMessageInfo(typeof(OrderCreatedEvent));
        var paymentInfo = _messages.GetMessageInfo(typeof(ProcessPaymentCommand));

        Assert.That(commandInfo?.Type, Is.EqualTo(MessageType.Command));
        Assert.That(eventInfo?.Type, Is.EqualTo(MessageType.Event));
        Assert.That(paymentInfo?.Endpoint, Is.EqualTo("PaymentService"));

        // Act & Assert - GetHeader
        var commandHeader = _messages.GetHeader(typeof(CreateOrderCommand));
        var eventHeader = _messages.GetHeader(typeof(OrderCreatedEvent));

        Assert.That(commandHeader, Does.Contain("OrderService"));
        Assert.That(eventHeader, Does.Contain("OrderCreated"));

        // Act & Assert - GetTypeByHeader
        var typeFromHeader = _messages.GetTypeByHeader(commandHeader!);
        Assert.That(typeFromHeader, Is.EqualTo(typeof(CreateOrderCommand)));
    }

    [Test]
    public void Add_SameTypeTwice_ThrowsArgumentException()
    {
        // Arrange
        _messages.Add(typeof(CreateOrderCommand));

        // Act & Assert
        Assert.Throws<ArgumentException>(() => _messages.Add(typeof(CreateOrderCommand)));
    }
}
