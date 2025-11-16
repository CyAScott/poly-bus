using NUnit.Framework;
using PolyBus.Transport.Transactions;

namespace PolyBus;

[TestFixture]
public class PolyBusTests
{
    [Test]
    public async Task IncomingHandlers_IsInvoked()
    {
        // Arrange
        var incomingTransactionTask = new TaskCompletionSource<IncomingTransaction>();
        var builder = new PolyBusBuilder
        {
            IncomingHandlers =
            {
                async (transaction, next) =>
                {
                    await next();
                    incomingTransactionTask.SetResult(transaction);
                }
            }
        };
        var bus = await builder.Build();

        // Act
        await bus.Start();
        var outgoingTransaction = await bus.CreateTransaction();
        outgoingTransaction.AddOutgoingMessage("Hello world", "unknown-endpoint");
        await outgoingTransaction.Commit();
        await bus.Start();
        var transaction = await incomingTransactionTask.Task;
        await Task.Yield();
        await bus.Stop();

        //Assert
        Assert.That(transaction.IncomingMessage.Body, Is.EqualTo("Hello world"));
    }

    [Test]
    public async Task IncomingHandlers_WithDelay_IsInvoked()
    {
        // Arrange
        var processedOnTask = new TaskCompletionSource<DateTime>();
        var builder = new PolyBusBuilder
        {
            IncomingHandlers =
            {
                async (_, next) =>
                {
                    await next();
                    processedOnTask.SetResult(DateTime.UtcNow);
                }
            }
        };
        var bus = await builder.Build();

        // Act
        await bus.Start();
        var outgoingTransaction = await bus.CreateTransaction();
        var message = outgoingTransaction.AddOutgoingMessage("Hello world", "unknown-endpoint");
        var scheduledAt = DateTime.UtcNow.AddSeconds(5);
        message.DeliverAt = scheduledAt;
        await outgoingTransaction.Commit();
        await bus.Start();
        var processedOn = await processedOnTask.Task;
        await Task.Yield();
        await bus.Stop();

        //Assert
        Assert.That(processedOn, Is.GreaterThanOrEqualTo(scheduledAt));
    }

    [Test]
    public async Task IncomingHandlers_WithDelayAndException_IsInvoked()
    {
        // Arrange
        var processedOnTask = new TaskCompletionSource<DateTime>();
        var builder = new PolyBusBuilder
        {
            IncomingHandlers =
            {
                (transaction, next) =>
                {
                    processedOnTask.SetResult(DateTime.UtcNow);
                    throw new Exception(transaction.IncomingMessage.Body);
                }
            }
        };
        var bus = await builder.Build();

        // Act
        await bus.Start();
        var outgoingTransaction = await bus.CreateTransaction();
        var message = outgoingTransaction.AddOutgoingMessage("Hello world", "unknown-endpoint");
        var scheduledAt = DateTime.UtcNow.AddSeconds(5);
        message.DeliverAt = scheduledAt;
        await outgoingTransaction.Commit();
        await bus.Start();
        var processedOn = await processedOnTask.Task;
        await Task.Yield();
        await bus.Stop();

        //Assert
        Assert.That(processedOn, Is.GreaterThanOrEqualTo(scheduledAt));
    }

    [Test]
    public async Task IncomingHandlers_WithException_IsInvoked()
    {
        // Arrange
        var incomingTransactionTask = new TaskCompletionSource<IncomingTransaction>();
        var builder = new PolyBusBuilder
        {
            IncomingHandlers =
            {
                (transaction, _) =>
                {
                    incomingTransactionTask.SetResult(transaction);
                    throw new Exception(transaction.IncomingMessage.Body);
                }
            }
        };
        var bus = await builder.Build();

        // Act
        await bus.Start();
        var outgoingTransaction = await bus.CreateTransaction();
        outgoingTransaction.AddOutgoingMessage("Hello world", "unknown-endpoint");
        await outgoingTransaction.Commit();
        await bus.Start();
        var transaction = await incomingTransactionTask.Task;
        await Task.Yield();
        await bus.Stop();

        //Assert
        Assert.That(transaction.IncomingMessage.Body, Is.EqualTo("Hello world"));
    }

    [Test]
    public async Task OutgoingHandlers_IsInvoked()
    {
        // Arrange
        var outgoingTransactionTask = new TaskCompletionSource<OutgoingTransaction>();
        var builder = new PolyBusBuilder
        {
            OutgoingHandlers =
            {
                async (transaction, next) =>
                {
                    await next();
                    outgoingTransactionTask.SetResult(transaction);
                }
            }
        };
        var bus = await builder.Build();

        // Act
        await bus.Start();
        var outgoingTransaction = await bus.CreateTransaction();
        outgoingTransaction.AddOutgoingMessage("Hello world", "unknown-endpoint");
        await outgoingTransaction.Commit();
        await bus.Start();
        var transaction = await outgoingTransactionTask.Task;
        await Task.Yield();
        await bus.Stop();

        //Assert
        Assert.That(transaction.OutgoingMessages.Count, Is.EqualTo(1));
        Assert.That(transaction.OutgoingMessages[0].Body, Is.EqualTo("Hello world"));
    }

    [Test]
    public async Task OutgoingHandlers_WithException_IsInvoked()
    {
        // Arrange
        var builder = new PolyBusBuilder
        {
            OutgoingHandlers =
            {
                (transaction, _) => throw new Exception(transaction.OutgoingMessages[0].Body)
            }
        };
        var bus = await builder.Build();

        // Act
        await bus.Start();
        var outgoingTransaction = await bus.CreateTransaction();
        outgoingTransaction.AddOutgoingMessage("Hello world", "unknown-endpoint");
        var ex = Assert.ThrowsAsync<Exception>(outgoingTransaction.Commit);
        await bus.Start();
        await bus.Stop();

        //Assert
        Assert.That(ex.Message, Is.EqualTo("Hello world"));
    }
}
