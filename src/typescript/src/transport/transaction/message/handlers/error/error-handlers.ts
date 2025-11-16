import { IncomingTransaction } from '../../../incoming-transaction';

/**
 * Handles error scenarios for message processing, including retries and dead letter queues.
 */
export class ErrorHandler {
  public static readonly ErrorMessageHeader = 'X-Error-Message';
  public static readonly ErrorStackTraceHeader = 'X-Error-Stack-Trace';
  public static readonly RetryCountHeader = 'X-Retry-Count';

  /**
   * The delay in seconds between retry attempts.
   * @default 30
   */
  public delay: number = 30;

  /**
   * The number of delayed retry attempts.
   * @default 3
   */
  public delayedRetryCount: number = 3;

  /**
   * The number of immediate retry attempts.
   * @default 3
   */
  public immediateRetryCount: number = 3;

  /**
   * The endpoint to send messages to when all retries are exhausted.
   * If not specified, defaults to {busName}.Errors
   */
  public deadLetterEndpoint?: string;

  /**
   * Retry handler that implements immediate and delayed retry logic.
   * @param transaction The incoming transaction to process.
   * @param next The next function in the pipeline to execute.
   */
  public async retrier(
    transaction: IncomingTransaction,
    next: () => Promise<void>
  ): Promise<void> {
    const headerValue = transaction.incomingMessage.headers.get(ErrorHandler.RetryCountHeader);
    const delayedAttempt = headerValue ? parseInt(headerValue, 10) || 0 : 0;
    const delayedRetryCount = Math.max(1, this.delayedRetryCount);
    const immediateRetryCount = Math.max(1, this.immediateRetryCount);

    for (let immediateAttempt = 0; immediateAttempt < immediateRetryCount; immediateAttempt++) {
      try {
        await next();
        break;
      } catch (error) {
        transaction.outgoingMessages.length = 0; // Clear outgoing messages

        if (immediateAttempt < immediateRetryCount - 1) {
          continue;
        }

        if (delayedAttempt < delayedRetryCount) {
          // Re-queue the message with a delay
          const nextDelayedAttempt = delayedAttempt + 1;

          const delayedMessage = transaction.addOutgoingMessage(
            transaction.incomingMessage.message,
            transaction.bus.name
          );
          delayedMessage.deliverAt = this.getNextRetryTime(nextDelayedAttempt);
          delayedMessage.headers.set(ErrorHandler.RetryCountHeader, nextDelayedAttempt.toString());

          continue;
        }

        const deadLetterEndpoint = this.deadLetterEndpoint ?? `${transaction.bus.name}.Errors`;
        const deadLetterMessage = transaction.addOutgoingMessage(
          transaction.incomingMessage.message,
          deadLetterEndpoint
        );
        deadLetterMessage.headers.set(ErrorHandler.ErrorMessageHeader, error instanceof Error ? error.message : String(error));
        deadLetterMessage.headers.set(
          ErrorHandler.ErrorStackTraceHeader,
          error instanceof Error ? error.stack ?? '' : ''
        );
      }
    }
  }

  /**
   * Calculates the next retry time based on the attempt number.
   * @param attempt The current attempt number.
   * @returns The Date when the next retry should be attempted.
   */
  public getNextRetryTime(attempt: number): Date {
    return new Date(Date.now() + attempt * this.delay * 1000);
  }
}
