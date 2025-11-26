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

    [Test]
    public void Add_ValidMessageType_ReturnsMessageInfo()
    {
        // Act
        var result = _messages.Add(typeof(Command));

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result.Type, Is.EqualTo(MessageType.Command));
        Assert.That(result.Endpoint, Is.EqualTo("polybus"));
        Assert.That(result.Name, Is.EqualTo("polybus-command"));
        Assert.That(result.Major, Is.EqualTo(1));
        Assert.That(result.Minor, Is.EqualTo(0));
        Assert.That(result.Patch, Is.EqualTo(0));
    }

    [Test]
    public void Add_MessageTypeWithoutAttribute_ThrowsError()
    {
        // Act & Assert
        Assert.Throws<PolyBusMessageNotFoundError>(() => _messages.Add(typeof(MessageWithoutAttribute)));
    }

    [Test]
    public void GetMessageInfo_ExistingType_ReturnsCorrectMessageInfo()
    {
        // Arrange
        _messages.Add(typeof(Command));

        // Act
        var result = _messages.GetMessageInfo(typeof(Command));

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result.Type, Is.EqualTo(MessageType.Command));
        Assert.That(result.Endpoint, Is.EqualTo("polybus"));
        Assert.That(result.Name, Is.EqualTo("polybus-command"));
    }

    [Test]
    public void GetMessageInfo_NonExistentType_ThrowsError()
    {
        // Act & Assert
        Assert.Throws<PolyBusMessageNotFoundError>(() => _messages.GetMessageInfo(typeof(Command)));
    }

    [Test]
    public void GetTypeByMessageInfo_ExistingMessageInfo_ReturnsCorrectType()
    {
        // Arrange
        _messages.Add(typeof(Event));
        var messageInfo = new MessageInfo(MessageType.Event, "polybus", "polybus-event", 2, 1, 3);

        // Act
        var result = _messages.GetTypeByMessageInfo(messageInfo);

        // Assert
        Assert.That(result, Is.EqualTo(typeof(Event)));
    }

    [Test]
    public void GetTypeByMessageInfo_NonExistentMessageInfo_ThrowsError()
    {
        // Arrange
        var messageInfo = new MessageInfo(MessageType.Command, "unknown", "unknown-command", 1, 0, 0);

        // Act & Assert
        Assert.Throws<PolyBusMessageNotFoundError>(() => _messages.GetTypeByMessageInfo(messageInfo));
    }

    [Test]
    public void GetTypeByMessageInfo_DifferentMinorPatchVersions_ReturnsType()
    {
        // Arrange
        _messages.Add(typeof(Event)); // Has version 2.1.3
        var messageInfoDifferentMinor = new MessageInfo(MessageType.Event, "polybus", "polybus-event", 2, 5, 3);
        var messageInfoDifferentPatch = new MessageInfo(MessageType.Event, "polybus", "polybus-event", 2, 1, 9);

        // Act
        var result1 = _messages.GetTypeByMessageInfo(messageInfoDifferentMinor);
        var result2 = _messages.GetTypeByMessageInfo(messageInfoDifferentPatch);

        // Assert
        Assert.That(result1, Is.EqualTo(typeof(Event)));
        Assert.That(result2, Is.EqualTo(typeof(Event)));
    }

    [Test]
    public void GetTypeByMessageInfo_DifferentMajorVersion_ThrowsError()
    {
        // Arrange
        _messages.Add(typeof(Event)); // Has version 2.1.3
        var messageInfoDifferentMajor = new MessageInfo(MessageType.Event, "polybus", "polybus-event", 3, 1, 3);

        // Act & Assert
        Assert.Throws<PolyBusMessageNotFoundError>(() => _messages.GetTypeByMessageInfo(messageInfoDifferentMajor));
    }

    [Test]
    public void Add_SameTypeTwice_ThrowsError()
    {
        // Arrange
        _messages.Add(typeof(Command));

        // Act & Assert
        Assert.Throws<PolyBusMessageNotFoundError>(() => _messages.Add(typeof(Command)));
    }

    [Test]
    public void GetHeaderByMessageInfo_ExistingMessageInfo_ReturnsCorrectHeader()
    {
        // Arrange
        _messages.Add(typeof(Command));
        var messageInfo = new MessageInfo(MessageType.Command, "polybus", "polybus-command", 1, 0, 0);

        // Act
        var result = _messages.GetHeaderByMessageInfo(messageInfo);

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Is.Not.Empty);
        Assert.That(result, Is.EqualTo(messageInfo.ToString(true)));
    }

    [Test]
    public void GetHeaderByMessageInfo_NonExistentMessageInfo_ThrowsError()
    {
        // Arrange
        var messageInfo = new MessageInfo(MessageType.Command, "unknown", "unknown-command", 1, 0, 0);

        // Act & Assert
        Assert.Throws<PolyBusMessageNotFoundError>(() => _messages.GetHeaderByMessageInfo(messageInfo));
    }

    [Test]
    public void GetHeaderByMessageInfo_DifferentMajorVersion_ThrowsError()
    {
        // Arrange
        _messages.Add(typeof(Event)); // Has version 2.1.3
        var messageInfoDifferentMajor = new MessageInfo(MessageType.Event, "polybus", "polybus-event", 3, 1, 3);

        // Act & Assert
        Assert.Throws<PolyBusMessageNotFoundError>(() => _messages.GetHeaderByMessageInfo(messageInfoDifferentMajor));
    }
}
