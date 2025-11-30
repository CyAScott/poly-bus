/* eslint-disable no-unused-vars */
import { describe, it, expect, beforeEach } from '@jest/globals';
import { ErrorHandler } from '../error-handlers';
import { IncomingTransaction } from '../../../../incoming-transaction';
import { IncomingMessage } from '../../../incoming-message';
import { IPolyBus } from '../../../../../../i-poly-bus';
import { ITransport } from '../../../../../i-transport';
import { Messages } from '../../../messages';
import { messageInfo } from '../../../message-info';
import { MessageType } from '../../../message-type';
import { IncomingHandler } from '../../incoming-handler';
import { OutgoingHandler } from '../../outgoing-handler';
import { Transaction } from '../../../../transaction';
import { OutgoingTransaction } from '../../../../outgoing-transaction';

// Test message class
@messageInfo(MessageType.Command, 'polybus', 'error-handler-test-message', 1, 0, 0)
class ErrorHandlerTestMessage {}

describe('ErrorHandler', () => {
  let testBus: IPolyBus;
  let incomingMessage: IncomingMessage;
  let transaction: IncomingTransaction;
  let errorHandler: TestableErrorHandler;

  beforeEach(() => {
    testBus = new TestBus('TestBus');
    testBus.messages.add(ErrorHandlerTestMessage);
    const messageInfo = testBus.messages.getMessageInfo(ErrorHandlerTestMessage);
    incomingMessage = new IncomingMessage(testBus, '{}', messageInfo);
    transaction = new IncomingTransaction(testBus, incomingMessage);
    errorHandler = new TestableErrorHandler();
  });

  it('Retrier_SucceedsOnFirstAttempt_DoesNotRetry', async () => {
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

  it('Retrier_FailsOnce_RetriesImmediately', async () => {
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

  it('Retrier_FailsAllImmediateRetries_SchedulesDelayedRetry', async () => {
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
    expect(delayedMessage.headers.get(errorHandler.retryCountHeader)).toBe('1');
    expect(delayedMessage.endpoint).toBe('TestBus');
  });

  it('Retrier_WithExistingRetryCount_IncrementsCorrectly', async () => {
    // Arrange
    incomingMessage.headers.set(errorHandler.retryCountHeader, '2');
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
    expect(delayedMessage.headers.get(errorHandler.retryCountHeader)).toBe('3');
    expect(delayedMessage.deliverAt).toEqual(expectedRetryTime);
  });

  it('Retrier_ExceedsMaxDelayedRetries_SendsToDeadLetter', async () => {
    // Arrange
    incomingMessage.headers.set(
      errorHandler.retryCountHeader,
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
    expect(deadLetterMessage.endpoint).toBe('dead-letters');
    expect(deadLetterMessage.headers.get(errorHandler.errorMessageHeader)).toBe('Final error');
    expect(deadLetterMessage.headers.get(errorHandler.errorStackTraceHeader)).toBeDefined();
  });

  it('Retrier_ClearsOutgoingMessagesOnEachRetry', async () => {
    // Arrange
    let callCount = 0;
    const next = async (): Promise<void> => {
      callCount++;
      transaction.add(new ErrorHandlerTestMessage());
      throw new Error('Test error');
    };

    // Act
    await errorHandler.retrier(transaction, next);

    // Assert
    expect(callCount).toBe(errorHandler.immediateRetryCount);
    // Should only have the delayed retry message, not the messages added in next()
    expect(transaction.outgoingMessages).toHaveLength(1);
    expect(transaction.outgoingMessages[0].headers.has(errorHandler.retryCountHeader)).toBe(true);
  });

  it('Retrier_WithZeroImmediateRetries_SchedulesDelayedRetryImmediately', async () => {
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
    expect(transaction.outgoingMessages[0].headers.get(errorHandler.retryCountHeader)).toBe('1');
  });

  it('Retrier_WithZeroDelayedRetries_StillGetsMinimumOfOne', async () => {
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
    expect(transaction.outgoingMessages[0].headers.get(errorHandler.retryCountHeader)).toBe('1');
    expect(transaction.outgoingMessages[0].deliverAt).toEqual(expectedRetryTime);
  });

  it('Retrier_SucceedsAfterSomeImmediateRetries_StopsRetrying', async () => {
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

  it('Retrier_InvalidRetryCountHeader_TreatsAsZero', async () => {
    // Arrange
    incomingMessage.headers.set(errorHandler.retryCountHeader, 'invalid');
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
    expect(delayedMessage.headers.get(errorHandler.retryCountHeader)).toBe('1');
  });

  it('Retrier_ExceptionStackTrace_IsStoredInHeader', async () => {
    // Arrange
    incomingMessage.headers.set(
      errorHandler.retryCountHeader,
      errorHandler.delayedRetryCount.toString()
    );

    const exceptionWithStackTrace = new Error('Error with stack trace');

    const next = async (): Promise<void> => {
      throw exceptionWithStackTrace;
    };

    // Act
    await errorHandler.retrier(transaction, next);

    // Assert
    expect(transaction.outgoingMessages).toHaveLength(1);
    const deadLetterMessage = transaction.outgoingMessages[0];
    expect(deadLetterMessage.headers.get(errorHandler.errorStackTraceHeader)).toBeDefined();
    expect(deadLetterMessage.headers.get(errorHandler.errorStackTraceHeader)).not.toBe('');
  });

  it('Retrier_ExceptionWithNullStackTrace_UsesEmptyString', async () => {
    // Arrange
    incomingMessage.headers.set(
      errorHandler.retryCountHeader,
      errorHandler.delayedRetryCount.toString()
    );

    // Create an exception with null StackTrace using custom exception
    const exceptionWithoutStackTrace = new ExceptionWithNullStackTrace('Error without stack trace');

    const next = async (): Promise<void> => {
      throw exceptionWithoutStackTrace;
    };

    // Act
    await errorHandler.retrier(transaction, next);

    // Assert
    expect(transaction.outgoingMessages).toHaveLength(1);
    const deadLetterMessage = transaction.outgoingMessages[0];
    expect(deadLetterMessage.headers.get(errorHandler.errorStackTraceHeader)).toBe('');
  });

  it('GetNextRetryTime_DefaultImplementation_UsesDelayCorrectly', () => {
    // Arrange
    const handler = new ErrorHandler();
    handler.delayIncrement = 60;
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

// Custom exception that returns null for StackTrace
class ExceptionWithNullStackTrace extends Error {
  constructor(message: string) {
    super(message);
    // Clear the stack trace by deleting the property
    delete (this as any).stack;
  }
}

// Test implementation of IPolyBus for testing purposes
class TestBus implements IPolyBus {
  public transport: ITransport;
  public incomingPipeline: IncomingHandler[] = [];
  public outgoingPipeline: OutgoingHandler[] = [];
  public messages: Messages = new Messages();
  public properties: Map<string, object> = new Map<string, object>();

  constructor(public name: string) {
    this.transport = new TestTransport();
  }

  public async createIncomingTransaction(message: IncomingMessage): Promise<IncomingTransaction> {
    return new IncomingTransaction(this, message);
  }

  public async createOutgoingTransaction(): Promise<OutgoingTransaction> {
    return new OutgoingTransaction(this);
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
  public readonly deadLetterEndpoint = 'dead-letters';
  public supportsCommandMessages = true;
  public supportsDelayedCommands = true;
  public supportsSubscriptions = false;

  public async handle(_transaction: Transaction): Promise<void> {
    // Mock implementation
  }

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
