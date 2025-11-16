using NUnit.Framework;

namespace PolyBus.Transport.Transactions.Messages.Handlers.Error;

[TestFixture]
public class ErrorHandlerTests
{
    private TestBus _testBus = null!;
    private IncomingMessage _incomingMessage = null!;
    private IncomingTransaction _transaction = null!;
    private TestableErrorHandler _errorHandler = null!;

    [SetUp]
    public void SetUp()
    {
        _testBus = new TestBus("TestBus");
        _incomingMessage = new IncomingMessage(_testBus, "test message body");
        _transaction = new IncomingTransaction(_testBus, _incomingMessage);
        _errorHandler = new TestableErrorHandler();
    }

    [Test]
    public async Task Retrier_SucceedsOnFirstAttempt_DoesNotRetry()
    {
        // Arrange
        var nextCalled = false;

        Task Next()
        {
            nextCalled = true;
            return Task.CompletedTask;
        }

        // Act
        await _errorHandler.Retrier(_transaction, Next);

        // Assert
        Assert.That(nextCalled, Is.True);
        Assert.That(_transaction.OutgoingMessages.Count, Is.EqualTo(0));
    }

    [Test]
    public async Task Retrier_FailsOnce_RetriesImmediately()
    {
        // Arrange
        var callCount = 0;

        Task Next()
        {
            callCount++;
            if (callCount == 1)
            {
                throw new Exception("Test error");
            }

            return Task.CompletedTask;
        }

        // Act
        await _errorHandler.Retrier(_transaction, Next);

        // Assert
        Assert.That(callCount, Is.EqualTo(2));
        Assert.That(_transaction.OutgoingMessages.Count, Is.EqualTo(0));
    }

    [Test]
    public async Task Retrier_FailsAllImmediateRetries_SchedulesDelayedRetry()
    {
        // Arrange
        var expectedRetryTime = DateTime.UtcNow.AddMinutes(5);
        _errorHandler.SetNextRetryTime(expectedRetryTime);

        var callCount = 0;

        Task Next()
        {
            callCount++;
            throw new Exception("Test error");
        }

        // Act
        await _errorHandler.Retrier(_transaction, Next);

        // Assert
        Assert.That(callCount, Is.EqualTo(_errorHandler.ImmediateRetryCount));
        Assert.That(_transaction.OutgoingMessages.Count, Is.EqualTo(1));

        var delayedMessage = _transaction.OutgoingMessages[0];
        Assert.That(delayedMessage.DeliverAt, Is.EqualTo(expectedRetryTime));
        Assert.That(delayedMessage.Headers[ErrorHandler.RetryCountHeader], Is.EqualTo("1"));
        Assert.That(delayedMessage.Endpoint, Is.EqualTo("TestBus"));
    }

    [Test]
    public async Task Retrier_WithExistingRetryCount_IncrementsCorrectly()
    {
        // Arrange
        _incomingMessage.Headers[ErrorHandler.RetryCountHeader] = "2";
        var expectedRetryTime = DateTime.UtcNow.AddMinutes(10);
        _errorHandler.SetNextRetryTime(expectedRetryTime);

        Task Next() => throw new Exception("Test error");

        // Act
        await _errorHandler.Retrier(_transaction, Next);

        // Assert
        Assert.That(_transaction.OutgoingMessages.Count, Is.EqualTo(1));

        var delayedMessage = _transaction.OutgoingMessages[0];
        Assert.That(delayedMessage.Headers[ErrorHandler.RetryCountHeader], Is.EqualTo("3"));
        Assert.That(delayedMessage.DeliverAt, Is.EqualTo(expectedRetryTime));
    }

    [Test]
    public async Task Retrier_ExceedsMaxDelayedRetries_SendsToDeadLetter()
    {
        // Arrange
        _incomingMessage.Headers[ErrorHandler.RetryCountHeader] =
            _errorHandler.DelayedRetryCount.ToString();

        var testException = new Exception("Final error");

        Task Next() => throw testException;

        // Act
        await _errorHandler.Retrier(_transaction, Next);

        // Assert
        Assert.That(_transaction.OutgoingMessages.Count, Is.EqualTo(1));

        var deadLetterMessage = _transaction.OutgoingMessages[0];
        Assert.That(deadLetterMessage.Endpoint, Is.EqualTo("TestBus.Errors"));
        Assert.That(deadLetterMessage.Headers[ErrorHandler.ErrorMessageHeader], Is.EqualTo("Final error"));
        Assert.That(deadLetterMessage.Headers[ErrorHandler.ErrorStackTraceHeader], Is.Not.Null);
    }

    [Test]
    public async Task Retrier_WithCustomDeadLetterEndpoint_UsesCustomEndpoint()
    {
        // Arrange
        _errorHandler = new TestableErrorHandler
        {
            DeadLetterEndpoint = "CustomDeadLetter"
        };

        _incomingMessage.Headers[ErrorHandler.RetryCountHeader] =
            _errorHandler.DelayedRetryCount.ToString();

        Task Next() => throw new Exception("Final error");

        // Act
        await _errorHandler.Retrier(_transaction, Next);

        // Assert
        Assert.That(_transaction.OutgoingMessages.Count, Is.EqualTo(1));

        var deadLetterMessage = _transaction.OutgoingMessages[0];
        Assert.That(deadLetterMessage.Endpoint, Is.EqualTo("CustomDeadLetter"));
    }

    [Test]
    public async Task Retrier_ClearsOutgoingMessagesOnEachRetry()
    {
        // Arrange
        var callCount = 0;

        Task Next()
        {
            callCount++;
            _transaction.AddOutgoingMessage("some message", "some endpoint");
            throw new Exception("Test error");
        }

        // Act
        await _errorHandler.Retrier(_transaction, Next);

        // Assert
        Assert.That(callCount, Is.EqualTo(_errorHandler.ImmediateRetryCount));
        // Should only have the delayed retry message, not the messages added in next()
        Assert.That(_transaction.OutgoingMessages.Count, Is.EqualTo(1));
        Assert.That(_transaction.OutgoingMessages[0].Headers.ContainsKey(ErrorHandler.RetryCountHeader), Is.True);
    }

    [Test]
    public async Task Retrier_WithZeroImmediateRetries_SchedulesDelayedRetryImmediately()
    {
        // Arrange
        _errorHandler = new TestableErrorHandler { ImmediateRetryCount = 0 };
        var expectedRetryTime = DateTime.UtcNow.AddMinutes(5);
        _errorHandler.SetNextRetryTime(expectedRetryTime);

        var callCount = 0;

        Task Next()
        {
            callCount++;
            throw new Exception("Test error");
        }

        // Act
        await _errorHandler.Retrier(_transaction, Next);

        // Assert
        Assert.That(callCount, Is.EqualTo(1)); // Should enforce minimum of 1
        Assert.That(_transaction.OutgoingMessages.Count, Is.EqualTo(1));
        Assert.That(_transaction.OutgoingMessages[0].Headers[ErrorHandler.RetryCountHeader], Is.EqualTo("1"));
    }

    [Test]
    public async Task Retrier_WithZeroDelayedRetries_StillGetsMinimumOfOne()
    {
        // Arrange
        _errorHandler = new TestableErrorHandler { DelayedRetryCount = 0 };
        var expectedRetryTime = DateTime.UtcNow.AddMinutes(5);
        _errorHandler.SetNextRetryTime(expectedRetryTime);

        Task Next() => throw new Exception("Test error");

        // Act
        await _errorHandler.Retrier(_transaction, Next);

        // Assert
        // Even with DelayedRetryCount = 0, Math.Max(1, DelayedRetryCount) makes it 1
        Assert.That(_transaction.OutgoingMessages.Count, Is.EqualTo(1));
        Assert.That(_transaction.OutgoingMessages[0].Headers[ErrorHandler.RetryCountHeader], Is.EqualTo("1"));
        Assert.That(_transaction.OutgoingMessages[0].DeliverAt, Is.EqualTo(expectedRetryTime));
    }

    [Test]
    public void GetNextRetryTime_DefaultImplementation_UsesDelayCorrectly()
    {
        // Arrange
        var handler = new ErrorHandler { Delay = 60 };
        var beforeTime = DateTime.UtcNow;

        // Act
        var result1 = handler.GetNextRetryTime(1);
        var result2 = handler.GetNextRetryTime(2);
        var result3 = handler.GetNextRetryTime(3);

        var afterTime = DateTime.UtcNow;

        // Assert
        Assert.That(result1, Is.GreaterThanOrEqualTo(beforeTime.AddSeconds(60)));
        Assert.That(result1, Is.LessThanOrEqualTo(afterTime.AddSeconds(60)));

        Assert.That(result2, Is.GreaterThanOrEqualTo(beforeTime.AddSeconds(120)));
        Assert.That(result2, Is.LessThanOrEqualTo(afterTime.AddSeconds(120)));

        Assert.That(result3, Is.GreaterThanOrEqualTo(beforeTime.AddSeconds(180)));
        Assert.That(result3, Is.LessThanOrEqualTo(afterTime.AddSeconds(180)));
    }

    [Test]
    public async Task Retrier_SucceedsAfterSomeImmediateRetries_StopsRetrying()
    {
        // Arrange
        var callCount = 0;

        Task Next()
        {
            callCount++;
            if (callCount < 3) // Fail first 2 attempts
            {
                throw new Exception("Test error");
            }

            return Task.CompletedTask;
        }

        // Act
        await _errorHandler.Retrier(_transaction, Next);

        // Assert
        Assert.That(callCount, Is.EqualTo(3));
        Assert.That(_transaction.OutgoingMessages.Count, Is.EqualTo(0));
    }

    [Test]
    public async Task Retrier_InvalidRetryCountHeader_TreatsAsZero()
    {
        // Arrange
        _incomingMessage.Headers[ErrorHandler.RetryCountHeader] = "invalid";
        var expectedRetryTime = DateTime.UtcNow.AddMinutes(5);
        _errorHandler.SetNextRetryTime(expectedRetryTime);

        Task Next() => throw new Exception("Test error");

        // Act
        await _errorHandler.Retrier(_transaction, Next);

        // Assert
        Assert.That(_transaction.OutgoingMessages.Count, Is.EqualTo(1));
        var delayedMessage = _transaction.OutgoingMessages[0];
        Assert.That(delayedMessage.Headers[ErrorHandler.RetryCountHeader], Is.EqualTo("1"));
    }

    [Test]
    public async Task Retrier_ExceptionStackTrace_IsStoredInHeader()
    {
        // Arrange
        _incomingMessage.Headers[ErrorHandler.RetryCountHeader] =
            _errorHandler.DelayedRetryCount.ToString();

        var exceptionWithStackTrace = new Exception("Error with stack trace");

        Task Next() => throw exceptionWithStackTrace;

        // Act
        await _errorHandler.Retrier(_transaction, Next);

        // Assert
        Assert.That(_transaction.OutgoingMessages.Count, Is.EqualTo(1));
        var deadLetterMessage = _transaction.OutgoingMessages[0];
        Assert.That(deadLetterMessage.Headers[ErrorHandler.ErrorStackTraceHeader], Is.Not.Null);
        Assert.That(deadLetterMessage.Headers[ErrorHandler.ErrorStackTraceHeader], Is.Not.Empty);
    }

    [Test]
    public async Task Retrier_ExceptionWithNullStackTrace_UsesEmptyString()
    {
        // Arrange
        _incomingMessage.Headers[ErrorHandler.RetryCountHeader] =
            _errorHandler.DelayedRetryCount.ToString();

        // Create an exception with null StackTrace using custom exception
        var exceptionWithoutStackTrace = new ExceptionWithNullStackTrace("Error without stack trace");

        Task Next() => throw exceptionWithoutStackTrace;

        // Act
        await _errorHandler.Retrier(_transaction, Next);

        // Assert
        Assert.That(_transaction.OutgoingMessages.Count, Is.EqualTo(1));
        var deadLetterMessage = _transaction.OutgoingMessages[0];
        Assert.That(deadLetterMessage.Headers[ErrorHandler.ErrorStackTraceHeader], Is.EqualTo(string.Empty));
    }

    // Helper class to override GetNextRetryTime for testing
    private class TestableErrorHandler : ErrorHandler
    {
        private DateTime? _nextRetryTime;

        public void SetNextRetryTime(DateTime retryTime)
        {
            _nextRetryTime = retryTime;
        }

        public override DateTime GetNextRetryTime(int attempt)
        {
            return _nextRetryTime ?? base.GetNextRetryTime(attempt);
        }
    }

    // Custom exception that returns null for StackTrace
    private class ExceptionWithNullStackTrace(string message) : Exception(message)
    {
        public override string? StackTrace => null;
    }

    // Test implementation of IPolyBus for testing purposes
    private class TestBus(string name) : IPolyBus
    {
        public IDictionary<string, object> Properties { get; } = new Dictionary<string, object>();
        public ITransport Transport { get; } = new TestTransport();
        public IList<IncomingHandler> IncomingHandlers { get; } = [];
        public IList<OutgoingHandler> OutgoingHandlers { get; } = [];
        public Messages Messages { get; } = new();
        public string Name { get; } = name;

        public Task<Transaction> CreateTransaction(IncomingMessage? message = null)
        {
            Transaction transaction = message == null
                ? new OutgoingTransaction(this)
                : new IncomingTransaction(this, message);
            return Task.FromResult(transaction);
        }

        public Task Send(Transaction transaction) => Task.CompletedTask;
        public Task Start() => Task.CompletedTask;
        public Task Stop() => Task.CompletedTask;
    }

    // Simple test transport implementation
    private class TestTransport : ITransport
    {
        public bool SupportsCommandMessages => true;
        public bool SupportsDelayedMessages => true;
        public bool SupportsSubscriptions => false;

        public Task Send(Transaction transaction) => Task.CompletedTask;
        public Task Subscribe(MessageInfo messageInfo) => Task.CompletedTask;
        public Task Start() => Task.CompletedTask;
        public Task Stop() => Task.CompletedTask;
    }
}
