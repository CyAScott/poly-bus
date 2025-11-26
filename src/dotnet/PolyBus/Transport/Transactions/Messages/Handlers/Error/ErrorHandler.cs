using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Abstractions;

namespace PolyBus.Transport.Transactions.Messages.Handlers.Error;

/// <summary>
/// A handler for processing message errors with retry logic.
/// </summary>
public class ErrorHandler
{
    /// <summary>
    /// The logger instance to use for logging.
    /// </summary>
    public ILogger<ErrorHandler> Log { get; set; } = NullLogger<ErrorHandler>.Instance;

    /// <summary>
    /// The delay increment in seconds for each delayed retry attempt.
    /// The delay is calculated as: delay attempt number * delay increment.
    /// </summary>
    public int DelayIncrement { get; set; } = 30;

    /// <summary>
    /// How many delayed retry attempts to make before sending to the dead-letter queue.
    /// </summary>
    public int DelayedRetryCount { get; set; } = 3;

    /// <summary>
    /// How many immediate retry attempts to make before applying delayed retries.
    /// </summary>
    public int ImmediateRetryCount { get; set; } = 3;

    /// <summary>
    /// The header key for storing error messages in dead-lettered messages.
    /// </summary>
    public string ErrorMessageHeader { get; set; } = "x-error-message";

    /// <summary>
    /// The header key for storing error stack traces in dead-lettered messages.
    /// </summary>
    public string ErrorStackTraceHeader { get; set; } = "x-error-stack-trace";

    /// <summary>
    /// The header key for storing the delayed retry count.
    /// </summary>
    public string RetryCountHeader { get; set; } = "x-retry-count";

    /// <summary>
    /// Retries the processing of a message according to the configured retry logic.
    /// </summary>
    public virtual async Task Retrier(IncomingTransaction transaction, Func<Task> next)
    {
        var delayedAttempt =
            transaction.IncomingMessage.Headers.TryGetValue(RetryCountHeader, out var headerValue)
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
                Log.LogError("Error processing message {MessageInfo} (immediate attempts: {immediateAttempt}, delayed attempts: {delayedAttempt}): {ErrorMessage}",
                    immediateAttempt,
                    delayedAttempt,
                    transaction.IncomingMessage.MessageInfo,
                    error.Message);

                transaction.OutgoingMessages.Clear();

                if (immediateAttempt < immediateRetryCount - 1)
                {
                    continue;
                }

                if (transaction.IncomingMessage.Bus.Transport.SupportsDelayedCommands
                    && delayedAttempt < delayedRetryCount)
                {
                    // Re-queue the message with a delay
                    delayedAttempt++;
                    var delayedMessage = new OutgoingMessage(
                        transaction.Bus,
                        transaction.IncomingMessage.Message,
                        transaction.Bus.Name,
                        transaction.IncomingMessage.MessageInfo)
                    {
                        DeliverAt = GetNextRetryTime(delayedAttempt),
                        Headers = transaction.IncomingMessage.Headers
                            .ToDictionary(it => it.Key, it => it.Value),
                    };
                    delayedMessage.Headers[RetryCountHeader] = delayedAttempt.ToString();
                    transaction.OutgoingMessages.Add(delayedMessage);

                    continue;
                }

                var deadLetterMessage = new OutgoingMessage(
                    transaction.Bus,
                    transaction.IncomingMessage.Message,
                    transaction.Bus.Transport.DeadLetterEndpoint,
                    transaction.IncomingMessage.MessageInfo)
                {
                    Headers = transaction.IncomingMessage.Headers
                        .ToDictionary(it => it.Key, it => it.Value),
                };
                deadLetterMessage.Headers[ErrorMessageHeader] = error.Message;
                deadLetterMessage.Headers[ErrorStackTraceHeader] = error.StackTrace ?? string.Empty;
                transaction.OutgoingMessages.Add(deadLetterMessage);
            }
        }
    }

    public virtual DateTime GetNextRetryTime(int attempt) => DateTime.UtcNow.AddSeconds(attempt * DelayIncrement);
}
