using System.Diagnostics;
using Microsoft.Extensions.Logging;
using NUnit.Framework;

namespace PolyBus.Transport.InMemory;

[TestFixture]
class InMemoryTransportTests
{
    private TestEnvironment _testEnvironment;

    [SetUp]
    public async Task SetUp()
    {
        _testEnvironment = new();
        await _testEnvironment.Setup();
    }

    [TearDown]
    public async Task TearDown()
    {
        await _testEnvironment.Stop();
    }

    [Test, CancelAfter(5 * 60 * 1000)]
    public async Task Send_BeforeStarting()
    {
        // Arrange
        var transaction = await _testEnvironment.Beta.Bus.CreateOutgoingTransaction();
        var taskCompletionSource = new TaskCompletionSource<bool>();
        _testEnvironment.Alpha.OnMessageReceived = _ =>
        {
            // This should not be called
            taskCompletionSource.SetResult(true);
            return Task.CompletedTask;
        };

        // Act
        transaction.Add(new AlphaCommand { Name = "Test" });

        // Assert - should throw an error because the transport is not started
        Assert.ThrowsAsync<PolyBusNotStartedError>(transaction.Commit);
        Assert.That(taskCompletionSource.Task.IsCompleted, Is.False);
    }

    [Test, CancelAfter(5 * 60 * 1000)]
    public async Task Send_AfterStarted()
    {
        // Arrange
        var transaction = await _testEnvironment.Beta.Bus.CreateOutgoingTransaction();
        var taskCompletionSource = new TaskCompletionSource<bool>();
        _testEnvironment.Alpha.OnMessageReceived = _ =>
        {
            taskCompletionSource.SetResult(true);
            return Task.CompletedTask;
        };

        // Act - send a command from the beta endpoint to alpha endpoint
        await _testEnvironment.Start();
        transaction.Add(new AlphaCommand { Name = "Test" });
        await transaction.Commit();
        await taskCompletionSource.Task;

        // Assert
        Assert.That(taskCompletionSource.Task.IsCompleted, Is.True);
    }

    [Test, CancelAfter(5 * 60 * 1000)]
    public async Task Send_WithExplicitEndpoint()
    {
        // Arrange
        var transaction = await _testEnvironment.Alpha.Bus.CreateOutgoingTransaction();
        var taskCompletionSource = new TaskCompletionSource<string>();
        _testEnvironment.Alpha.OnMessageReceived = arg =>
        {
            // This should NOT be called
            taskCompletionSource.SetResult(arg.Bus.Name);
            return Task.CompletedTask;
        };
        _testEnvironment.Alpha.Transport.DeadLetterHandler = _ =>
        {
            // This should be called
            taskCompletionSource.SetResult(_testEnvironment.Alpha.Transport.DeadLetterEndpoint);
        };
        var endpoint = _testEnvironment.Alpha.Transport.DeadLetterEndpoint;

        // Act - send the alpha command to beta endpoint
        await _testEnvironment.Start();
        transaction.Add(new AlphaCommand { Name = "Test" }, endpoint: endpoint);
        await transaction.Commit();
        var actualEndpoint = await taskCompletionSource.Task;

        // Assert
        Assert.That(actualEndpoint, Is.EqualTo(endpoint));
    }

    [Test, CancelAfter(5 * 60 * 1000)]
    public async Task Send_WithHeaders()
    {
        // Arrange
        const string headerKey = "X-Custom-Header";
        const string headerValue = "HeaderValue";
        var transaction = await _testEnvironment.Alpha.Bus.CreateOutgoingTransaction();
        var taskCompletionSource = new TaskCompletionSource<string>();
        _testEnvironment.Alpha.OnMessageReceived = message =>
        {
            taskCompletionSource.SetResult(
                message.IncomingMessage.Headers.TryGetValue(headerKey, out var value)
                ? value
                : string.Empty);
            return Task.CompletedTask;
        };

        // Act - send a command with a custom header
        await _testEnvironment.Start();
        var message = transaction.Add(new AlphaCommand { Name = "Test" });
        message.Headers.Add(headerKey, headerValue);
        await transaction.Commit();
        var actualHeaderValue = await taskCompletionSource.Task;

        // Assert
        Assert.That(actualHeaderValue, Is.EqualTo(headerValue));
    }

    [Test, CancelAfter(5 * 60 * 1000)]
    public async Task Send_WithDelay()
    {
        // Arrange
        const int delay = 5000; // 5 seconds
        var transaction = await _testEnvironment.Alpha.Bus.CreateOutgoingTransaction();
        var stopwatch = new Stopwatch();
        var taskCompletionSource = new TaskCompletionSource<TimeSpan>();
        _testEnvironment.Alpha.OnMessageReceived = _ =>
        {
            stopwatch.Stop();
            taskCompletionSource.SetResult(stopwatch.Elapsed);
            return Task.CompletedTask;
        };

        // Act - send to the dead letters queue instead of normal processing queue
        await _testEnvironment.Start();
        var message = transaction.Add(new AlphaCommand { Name = "Test" });
        message.DeliverAt = DateTime.UtcNow.AddMilliseconds(delay);
        stopwatch.Start();
        await transaction.Commit();
        var elapsed = await taskCompletionSource.Task;
        _testEnvironment.InMemoryMessageBroker.Log.LogInformation("Elapsed time for delayed message: {Elapsed}",
            Math.Floor(elapsed.TotalMilliseconds));

        // Assert
        Assert.That(elapsed, Is
            .LessThanOrEqualTo(TimeSpan.FromMilliseconds(delay + 1000)) // allow 1 second of leeway
            .And.GreaterThanOrEqualTo(TimeSpan.FromMilliseconds(delay - 1000)));// allow 1 second of leeway
    }

    [Test, CancelAfter(5 * 60 * 1000)]
    public async Task Send_WithExpiredDelay()
    {
        // Arrange
        var transaction = await _testEnvironment.Alpha.Bus.CreateOutgoingTransaction();
        var taskCompletionSource = new TaskCompletionSource<bool>();
        _testEnvironment.Alpha.OnMessageReceived = _ =>
        {
            taskCompletionSource.SetResult(true);
            return Task.CompletedTask;
        };

        // Act - schedule command to be delivered in the past
        await _testEnvironment.Start();
        var message = transaction.Add(new AlphaCommand { Name = "Test" });
        message.DeliverAt = DateTime.UtcNow.AddMilliseconds(-1000); // 1 second in the past
        await transaction.Commit();
        await taskCompletionSource.Task;

        // Assert
        Assert.That(taskCompletionSource.Task.IsCompleted, Is.True);
    }

    [Test, CancelAfter(5 * 60 * 1000)]
    public async Task Start_WhenAlreadyStarted()
    {
        // Act
        await _testEnvironment.Start();

        // Assert - starting again should not throw an error
        Assert.DoesNotThrowAsync(_testEnvironment.Start);
    }

    [Test, CancelAfter(5 * 60 * 1000)]
    public async Task Subscribe_BeforeStarted()
    {
        // Arrange
        var transaction = await _testEnvironment.Alpha.Bus.CreateOutgoingTransaction();
        var taskCompletionSource = new TaskCompletionSource<bool>();
        _testEnvironment.Beta.OnMessageReceived = _ =>
        {
            taskCompletionSource.SetResult(true);
            return Task.CompletedTask;
        };

        // Act - subscribing before starting should throw an error
        Assert.ThrowsAsync<PolyBusNotStartedError>(async () =>
        {
            await _testEnvironment.Beta.Transport.Subscribe(
                _testEnvironment.Beta.Bus.Messages.GetMessageInfo(typeof(AlphaEvent))!);
        });
        transaction.Add(new AlphaEvent { Name = "Test" });
        Assert.ThrowsAsync<PolyBusNotStartedError>(transaction.Commit);

        // Assert
        Assert.That(taskCompletionSource.Task.IsCompleted, Is.False);
    }

    [Test, CancelAfter(5 * 60 * 1000)]
    public async Task Subscribe()
    {
        // Arrange
        var transaction = await _testEnvironment.Alpha.Bus.CreateOutgoingTransaction();
        var taskCompletionSource = new TaskCompletionSource<bool>();
        _testEnvironment.Beta.OnMessageReceived = _ =>
        {
            taskCompletionSource.SetResult(true);
            return Task.CompletedTask;
        };
        await _testEnvironment.Start();

        // Act - subscribing before starting should throw an error
        await _testEnvironment.Beta.Transport.Subscribe(
            _testEnvironment.Beta.Bus.Messages.GetMessageInfo(typeof(AlphaEvent))!);
        transaction.Add(new AlphaEvent { Name = "Test" });
        await transaction.Commit();
        await taskCompletionSource.Task;
    }
}
