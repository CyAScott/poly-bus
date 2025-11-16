namespace PolyBus.Transport.Transactions.Messages.Handlers.Error;

public class ErrorHandler
{
    public const string ErrorMessageHeader = "X-Error-Message";
    public const string ErrorStackTraceHeader = "X-Error-Stack-Trace";
    public const string RetryCountHeader = "X-Retry-Count";

    public int Delay { get; set; } = 30;

    public int DelayedRetryCount { get; set; } = 3;

    public int ImmediateRetryCount { get; set; } = 3;

    public string? DeadLetterEndpoint { get; set; }

    public async Task Retrier(IncomingTransaction transaction, Func<Task> next)
    {
        var delayedAttempt = transaction.IncomingMessage.Headers.TryGetValue(RetryCountHeader, out var headerValue)
                      && byte.TryParse(headerValue, out var parsedHeaderValue)
                ? parsedHeaderValue
                : 0;
        var delayedRetryCount = Math.Max(1, DelayedRetryCount);
        var immediateRetryCount = Math.Max(1, ImmediateRetryCount);

        for (var immediateAttempt = 0; immediateAttempt < immediateRetryCount; immediateAttempt++)
        {
            try
            {
                await next();
                break;
            }
            catch (Exception error)
            {
                transaction.OutgoingMessages.Clear();

                if (immediateAttempt < immediateRetryCount - 1)
                {
                    continue;
                }

                if (delayedAttempt < delayedRetryCount)
                {
                    // Re-queue the message with a delay
                    delayedAttempt++;

                    var delayedMessage = transaction.AddOutgoingMessage(
                        transaction.IncomingMessage,
                        transaction.Bus.Name);
                    delayedMessage.DeliverAt = GetNextRetryTime(delayedAttempt);
                    delayedMessage.Headers[RetryCountHeader] = delayedAttempt.ToString();

                    continue;
                }

                var deadLetterEndpoint = DeadLetterEndpoint ?? $"{transaction.Bus.Name}.Errors";
                var deadLetterMessage = transaction.AddOutgoingMessage(transaction.IncomingMessage, deadLetterEndpoint);
                deadLetterMessage.Headers[ErrorMessageHeader] = error.Message;
                deadLetterMessage.Headers[ErrorStackTraceHeader] = error.StackTrace ?? string.Empty;
            }
        }
    }

    public virtual DateTime GetNextRetryTime(int attempt) => DateTime.UtcNow.AddSeconds(attempt * Delay);
}
