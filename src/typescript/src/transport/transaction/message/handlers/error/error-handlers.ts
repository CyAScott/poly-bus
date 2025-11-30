import { IncomingTransaction } from '../../../incoming-transaction';
import { OutgoingMessage } from '../../outgoing-message';

/**
 * A handler for processing message errors with retry logic.
 */
export class ErrorHandler {
  /**
   * The logger instance to use for logging.
   */
  public log: typeof console = console;

  /**
   * The delay increment in seconds for each delayed retry attempt.
   * The delay is calculated as: delay attempt number * delay increment.
   */
  public delayIncrement: number = 30;

  /**
   * How many delayed retry attempts to make before sending to the dead-letter queue.
   */
  public delayedRetryCount: number = 3;

  /**
   * How many immediate retry attempts to make before applying delayed retries.
   */
  public immediateRetryCount: number = 3;

  /**
   * The header key for storing error messages in dead-lettered messages.
   */
  public errorMessageHeader: string = 'x-error-message';

  /**
   * The header key for storing error stack traces in dead-lettered messages.
   */
  public errorStackTraceHeader: string = 'x-error-stack-trace';

  /**
   * The header key for storing the delayed retry count.
   */
  public retryCountHeader: string = 'x-retry-count';

  /**
   * Retries the processing of a message according to the configured retry logic.
   */
  public async retrier(
    transaction: IncomingTransaction,
    next: () => Promise<void>
  ): Promise<void> {
    const headerValue = transaction.incomingMessage.headers.get(this.retryCountHeader);
    let delayedAttempt = headerValue ? parseInt(headerValue, 10) || 0 : 0;
    const delayedRetryCount = Math.max(1, this.delayedRetryCount);
    const immediateRetryCount = Math.max(1, this.immediateRetryCount);

    for (let immediateAttempt = 0; immediateAttempt < immediateRetryCount; immediateAttempt++) {
      try {
        await next();
        break;
      } catch (error) {
        this.log.error(
          `Error processing message ${transaction.incomingMessage.messageInfo} (immediate attempts: ${immediateAttempt}, delayed attempts: ${delayedAttempt}): ${error instanceof Error ? error.message : String(error)}`
        );

        transaction.outgoingMessages.length = 0;

        if (immediateAttempt < immediateRetryCount - 1) {
          continue;
        }

        if (transaction.incomingMessage.bus.transport.supportsDelayedCommands
          && delayedAttempt < delayedRetryCount) {
          // Re-queue the message with a delay
          delayedAttempt++;
          const delayedMessage = new OutgoingMessage(
            transaction.bus,
            transaction.incomingMessage.message,
            transaction.bus.name,
            transaction.incomingMessage.messageInfo
          );
          delayedMessage.deliverAt = this.getNextRetryTime(delayedAttempt);
          transaction.incomingMessage.headers.forEach((value, key) => {
            delayedMessage.headers.set(key, value);
          });
          delayedMessage.headers.set(this.retryCountHeader, delayedAttempt.toString());
          transaction.outgoingMessages.push(delayedMessage);

          continue;
        }

        const deadLetterMessage = new OutgoingMessage(
          transaction.bus,
          transaction.incomingMessage.message,
          transaction.bus.transport.deadLetterEndpoint,
          transaction.incomingMessage.messageInfo
        );
        transaction.incomingMessage.headers.forEach((value, key) => {
          deadLetterMessage.headers.set(key, value);
        });
        deadLetterMessage.headers.set(this.errorMessageHeader, error instanceof Error ? error.message : String(error));
        deadLetterMessage.headers.set(
          this.errorStackTraceHeader,
          error instanceof Error ? error.stack ?? '' : ''
        );
        transaction.outgoingMessages.push(deadLetterMessage);
      }
    }
  }

  public getNextRetryTime(attempt: number): Date {
    return new Date(Date.now() + attempt * this.delayIncrement * 1000);
  }
}
