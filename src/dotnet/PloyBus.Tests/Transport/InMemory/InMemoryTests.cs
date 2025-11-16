using System.Reflection;
using NUnit.Framework;
using PolyBus.Transport.Transactions;
using PolyBus.Transport.Transactions.Messages;

namespace PolyBus.Transport.InMemory;

[TestFixture]
public class InMemoryTests
{
    private readonly MessageInfo _messageInfo = typeof(TestMessage).GetCustomAttribute<MessageInfo>()!;

    [Test]
    public async Task InMemory_WithSubscription()
    {
        // Arrange
        var inMemoryTransport = new InMemoryTransport
        {
            UseSubscriptions = true
        };
        var incomingTransactionTask = new TaskCompletionSource<IncomingTransaction>();
        var builder = new PolyBusBuilder
        {
            IncomingHandlers =
            {
                async (transaction, next) =>
                {
                    incomingTransactionTask.SetResult(transaction);
                    await next();
                }
            },
            TransportFactory = (builder, bus) => Task.FromResult(inMemoryTransport.AddEndpoint(builder, bus))
        };
        builder.Messages.Add(typeof(TestMessage));
        var bus = await builder.Build();
        await bus.Transport.Subscribe(typeof(TestMessage).GetCustomAttribute<MessageInfo>()!);

        // Act
        await bus.Start();
        var outgoingTransaction = await bus.CreateTransaction();
        var outgoingMessage = outgoingTransaction.AddOutgoingMessage(new TestMessage
        {
            Name = "TestMessage"
        });
        outgoingMessage.Headers[Headers.MessageType] = _messageInfo.ToString(true);
        await outgoingTransaction.Commit();
        await bus.Start();
        var incomingTransaction = await incomingTransactionTask.Task;
        await Task.Yield();
        await bus.Stop();

        //Assert
        Assert.That(incomingTransaction.IncomingMessage.Body, Is.EqualTo("TestMessage"));
        Assert.That(incomingTransaction.IncomingMessage.Headers[Headers.MessageType], Is.EqualTo(_messageInfo.ToString(true)));
    }

    [MessageInfo(MessageType.Command, "test-service", "TestMessage", 1, 0, 0)]
    public class TestMessage
    {
        public override string ToString() => Name;
        public required string Name { get; init; } = string.Empty;
    }
}
