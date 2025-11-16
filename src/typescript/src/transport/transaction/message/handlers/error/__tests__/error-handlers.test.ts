import { describe, it, expect, beforeEach } from '@jest/globals';
import { ErrorHandler } from '../error-handlers';
import { IncomingTransaction } from '../../../../incoming-transaction';
import { IncomingMessage } from '../../../incoming-message';
import { IPolyBus } from '../../../../../../i-poly-bus';
import { ITransport } from '../../../../../i-transport';
import { Messages } from '../../../messages';
import { IncomingHandler } from '../../incoming-handler';
import { OutgoingHandler } from '../../outgoing-handler';
import { Transaction } from '../../../../transaction';
import { OutgoingTransaction } from '../../../../outgoing-transaction';

describe('ErrorHandler', () => {
  let testBus: IPolyBus;
  let incomingMessage: IncomingMessage;
  let transaction: IncomingTransaction;
  let errorHandler: TestableErrorHandler;

  beforeEach(() => {
    testBus = new TestBus('TestBus');
    incomingMessage = new IncomingMessage(testBus, 'test message body');
    transaction = new IncomingTransaction(testBus, incomingMessage);
    errorHandler = new TestableErrorHandler();
  });

  describe('retrier method', () => {
    it('should succeed on first attempt and not retry', async () => {
      // Arrange
      let nextCalled = false;
      const next = async (): Promise<void> => {
        nextCalled = true;
      };

      // Act
      await errorHandler.retrier(transaction, next);

      // Assert
      expect(nextCalled).toBe(true);
      expect(transaction.outgoingMessages).toHaveLength(0);
    });

    it('should fail once and retry immediately', async () => {
      // Arrange
      let callCount = 0;
      const next = async (): Promise<void> => {
        callCount++;
        if (callCount === 1) {
          throw new Error('Test error');
        }
      };

      // Act
      await errorHandler.retrier(transaction, next);

      // Assert
      expect(callCount).toBe(2);
      expect(transaction.outgoingMessages).toHaveLength(0);
    });

    it('should fail all immediate retries and schedule delayed retry', async () => {
      // Arrange
      const expectedRetryTime = new Date(Date.now() + 5 * 60 * 1000); // 5 minutes from now
      errorHandler.setNextRetryTime(expectedRetryTime);

      let callCount = 0;
      const next = async (): Promise<void> => {
        callCount++;
        throw new Error('Test error');
      };

      // Act
      await errorHandler.retrier(transaction, next);

      // Assert
      expect(callCount).toBe(errorHandler.immediateRetryCount);
      expect(transaction.outgoingMessages).toHaveLength(1);

      const delayedMessage = transaction.outgoingMessages[0];
      expect(delayedMessage.deliverAt).toEqual(expectedRetryTime);
      expect(delayedMessage.headers.get(ErrorHandler.RetryCountHeader)).toBe('1');
      expect(delayedMessage.endpoint).toBe('TestBus');
    });

    it('should increment retry count correctly when existing retry count header exists', async () => {
      // Arrange
      incomingMessage.headers.set(ErrorHandler.RetryCountHeader, '2');
      const expectedRetryTime = new Date(Date.now() + 10 * 60 * 1000); // 10 minutes from now
      errorHandler.setNextRetryTime(expectedRetryTime);

      const next = async (): Promise<void> => {
        throw new Error('Test error');
      };

      // Act
      await errorHandler.retrier(transaction, next);

      // Assert
      expect(transaction.outgoingMessages).toHaveLength(1);

      const delayedMessage = transaction.outgoingMessages[0];
      expect(delayedMessage.headers.get(ErrorHandler.RetryCountHeader)).toBe('3');
      expect(delayedMessage.deliverAt).toEqual(expectedRetryTime);
    });

    it('should send to dead letter queue when max delayed retries exceeded', async () => {
      // Arrange
      incomingMessage.headers.set(
        ErrorHandler.RetryCountHeader,
        errorHandler.delayedRetryCount.toString()
      );

      const testException = new Error('Final error');
      const next = async (): Promise<void> => {
        throw testException;
      };

      // Act
      await errorHandler.retrier(transaction, next);

      // Assert
      expect(transaction.outgoingMessages).toHaveLength(1);

      const deadLetterMessage = transaction.outgoingMessages[0];
      expect(deadLetterMessage.endpoint).toBe('TestBus.Errors');
      expect(deadLetterMessage.headers.get(ErrorHandler.ErrorMessageHeader)).toBe('Final error');
      expect(deadLetterMessage.headers.get(ErrorHandler.ErrorStackTraceHeader)).toBeDefined();
    });

    it('should use custom dead letter endpoint when specified', async () => {
      // Arrange
      errorHandler = new TestableErrorHandler();
      errorHandler.deadLetterEndpoint = 'CustomDeadLetter';

      incomingMessage.headers.set(
        ErrorHandler.RetryCountHeader,
        errorHandler.delayedRetryCount.toString()
      );

      const next = async (): Promise<void> => {
        throw new Error('Final error');
      };

      // Act
      await errorHandler.retrier(transaction, next);

      // Assert
      expect(transaction.outgoingMessages).toHaveLength(1);

      const deadLetterMessage = transaction.outgoingMessages[0];
      expect(deadLetterMessage.endpoint).toBe('CustomDeadLetter');
    });

    it('should clear outgoing messages on each retry', async () => {
      // Arrange
      let callCount = 0;
      const next = async (): Promise<void> => {
        callCount++;
        transaction.addOutgoingMessage('some message', 'some endpoint');
        throw new Error('Test error');
      };

      // Act
      await errorHandler.retrier(transaction, next);

      // Assert
      expect(callCount).toBe(errorHandler.immediateRetryCount);
      // Should only have the delayed retry message, not the messages added in next()
      expect(transaction.outgoingMessages).toHaveLength(1);
      expect(transaction.outgoingMessages[0].headers.has(ErrorHandler.RetryCountHeader)).toBe(true);
    });

    it('should handle zero immediate retries with minimum of one', async () => {
      // Arrange
      errorHandler = new TestableErrorHandler();
      errorHandler.immediateRetryCount = 0;
      const expectedRetryTime = new Date(Date.now() + 5 * 60 * 1000);
      errorHandler.setNextRetryTime(expectedRetryTime);

      let callCount = 0;
      const next = async (): Promise<void> => {
        callCount++;
        throw new Error('Test error');
      };

      // Act
      await errorHandler.retrier(transaction, next);

      // Assert
      expect(callCount).toBe(1); // Should enforce minimum of 1
      expect(transaction.outgoingMessages).toHaveLength(1);
      expect(transaction.outgoingMessages[0].headers.get(ErrorHandler.RetryCountHeader)).toBe('1');
    });

    it('should handle zero delayed retries with minimum of one', async () => {
      // Arrange
      errorHandler = new TestableErrorHandler();
      errorHandler.delayedRetryCount = 0;
      const expectedRetryTime = new Date(Date.now() + 5 * 60 * 1000);
      errorHandler.setNextRetryTime(expectedRetryTime);

      const next = async (): Promise<void> => {
        throw new Error('Test error');
      };

      // Act
      await errorHandler.retrier(transaction, next);

      // Assert
      // Even with delayedRetryCount = 0, Math.max(1, delayedRetryCount) makes it 1
      expect(transaction.outgoingMessages).toHaveLength(1);
      expect(transaction.outgoingMessages[0].headers.get(ErrorHandler.RetryCountHeader)).toBe('1');
      expect(transaction.outgoingMessages[0].deliverAt).toEqual(expectedRetryTime);
    });

    it('should succeed after some immediate retries and stop retrying', async () => {
      // Arrange
      let callCount = 0;
      const next = async (): Promise<void> => {
        callCount++;
        if (callCount < 3) { // Fail first 2 attempts
          throw new Error('Test error');
        }
      };

      // Act
      await errorHandler.retrier(transaction, next);

      // Assert
      expect(callCount).toBe(3);
      expect(transaction.outgoingMessages).toHaveLength(0);
    });

    it('should treat invalid retry count header as zero', async () => {
      // Arrange
      incomingMessage.headers.set(ErrorHandler.RetryCountHeader, 'invalid');
      const expectedRetryTime = new Date(Date.now() + 5 * 60 * 1000);
      errorHandler.setNextRetryTime(expectedRetryTime);

      const next = async (): Promise<void> => {
        throw new Error('Test error');
      };

      // Act
      await errorHandler.retrier(transaction, next);

      // Assert
      expect(transaction.outgoingMessages).toHaveLength(1);
      const delayedMessage = transaction.outgoingMessages[0];
      expect(delayedMessage.headers.get(ErrorHandler.RetryCountHeader)).toBe('1');
    });

    it('should store error stack trace in header', async () => {
      // Arrange
      incomingMessage.headers.set(
        ErrorHandler.RetryCountHeader,
        errorHandler.delayedRetryCount.toString()
      );

      const errorWithStackTrace = new Error('Error with stack trace');

      const next = async (): Promise<void> => {
        throw errorWithStackTrace;
      };

      // Act
      await errorHandler.retrier(transaction, next);

      // Assert
      expect(transaction.outgoingMessages).toHaveLength(1);
      const deadLetterMessage = transaction.outgoingMessages[0];
      expect(deadLetterMessage.headers.get(ErrorHandler.ErrorStackTraceHeader)).toBeDefined();
      expect(deadLetterMessage.headers.get(ErrorHandler.ErrorStackTraceHeader)).not.toBe('');
    });

    it('should use empty string for null stack trace', async () => {
      // Arrange
      incomingMessage.headers.set(
        ErrorHandler.RetryCountHeader,
        errorHandler.delayedRetryCount.toString()
      );

      // Create an error with null stack trace using custom error
      const errorWithoutStackTrace = new ErrorWithNullStackTrace('Error without stack trace');

      const next = async (): Promise<void> => {
        throw errorWithoutStackTrace;
      };

      // Act
      await errorHandler.retrier(transaction, next);

      // Assert
      expect(transaction.outgoingMessages).toHaveLength(1);
      const deadLetterMessage = transaction.outgoingMessages[0];
      expect(deadLetterMessage.headers.get(ErrorHandler.ErrorStackTraceHeader)).toBe('');
    });

    it('should handle non-Error exceptions', async () => {
      // Arrange
      incomingMessage.headers.set(
        ErrorHandler.RetryCountHeader,
        errorHandler.delayedRetryCount.toString()
      );

      const next = async (): Promise<void> => {
        throw 'String error'; // eslint-disable-line @typescript-eslint/no-throw-literal
      };

      // Act
      await errorHandler.retrier(transaction, next);

      // Assert
      expect(transaction.outgoingMessages).toHaveLength(1);
      const deadLetterMessage = transaction.outgoingMessages[0];
      expect(deadLetterMessage.headers.get(ErrorHandler.ErrorMessageHeader)).toBe('String error');
      expect(deadLetterMessage.headers.get(ErrorHandler.ErrorStackTraceHeader)).toBe('');
    });
  });

  describe('getNextRetryTime method', () => {
    it('should calculate retry time correctly with default delay', () => {
      // Arrange
      const handler = new ErrorHandler();
      handler.delay = 60;
      const beforeTime = new Date();

      // Act
      const result1 = handler.getNextRetryTime(1);
      const result2 = handler.getNextRetryTime(2);
      const result3 = handler.getNextRetryTime(3);

      const afterTime = new Date();

      // Assert
      expect(result1.getTime()).toBeGreaterThanOrEqual(beforeTime.getTime() + 60 * 1000);
      expect(result1.getTime()).toBeLessThanOrEqual(afterTime.getTime() + 60 * 1000);

      expect(result2.getTime()).toBeGreaterThanOrEqual(beforeTime.getTime() + 120 * 1000);
      expect(result2.getTime()).toBeLessThanOrEqual(afterTime.getTime() + 120 * 1000);

      expect(result3.getTime()).toBeGreaterThanOrEqual(beforeTime.getTime() + 180 * 1000);
      expect(result3.getTime()).toBeLessThanOrEqual(afterTime.getTime() + 180 * 1000);
    });
  });

  describe('static constants', () => {
    it('should have correct error header constants', () => {
      expect(ErrorHandler.ErrorMessageHeader).toBe('X-Error-Message');
      expect(ErrorHandler.ErrorStackTraceHeader).toBe('X-Error-Stack-Trace');
      expect(ErrorHandler.RetryCountHeader).toBe('X-Retry-Count');
    });
  });

  describe('default configuration', () => {
    it('should have correct default values', () => {
      const handler = new ErrorHandler();
      expect(handler.delay).toBe(30);
      expect(handler.delayedRetryCount).toBe(3);
      expect(handler.immediateRetryCount).toBe(3);
      expect(handler.deadLetterEndpoint).toBeUndefined();
    });
  });
});

// Helper class to override getNextRetryTime for testing
class TestableErrorHandler extends ErrorHandler {
  private nextRetryTime?: Date;

  public setNextRetryTime(retryTime: Date): void {
    this.nextRetryTime = retryTime;
  }

  public override getNextRetryTime(attempt: number): Date {
    return this.nextRetryTime ?? super.getNextRetryTime(attempt);
  }
}

// Custom error that returns undefined for stack trace
class ErrorWithNullStackTrace extends Error {
  constructor(message: string) {
    super(message);
    // Clear the stack trace by deleting the property
    delete (this as any).stack;
  }
}

// Test implementation of IPolyBus for testing purposes
class TestBus implements IPolyBus {
  public transport: ITransport;
  public incomingHandlers: IncomingHandler[] = [];
  public outgoingHandlers: OutgoingHandler[] = [];
  public messages: Messages = new Messages();
  public properties: Map<string, object> = new Map<string, object>();

  constructor(public name: string) {
    this.transport = new TestTransport();
  }

  public async createTransaction(message?: IncomingMessage): Promise<Transaction> {
    const transaction: Transaction = message == null
      ? new OutgoingTransaction(this)
      : new IncomingTransaction(this, message);
    return transaction;
  }

  public async send(_transaction: Transaction): Promise<void> {
    // Mock implementation
  }

  public async start(): Promise<void> {
    // Mock implementation
  }

  public async stop(): Promise<void> {
    // Mock implementation
  }
}

// Simple test transport implementation
class TestTransport implements ITransport {
  public supportsCommandMessages = true;
  public supportsDelayedMessages = true;
  public supportsSubscriptions = false;

  public async send(_transaction: Transaction): Promise<void> {
    // Mock implementation
  }

  public async subscribe(): Promise<void> {
    // Mock implementation
  }

  public async start(): Promise<void> {
    // Mock implementation
  }

  public async stop(): Promise<void> {
    // Mock implementation
  }
}