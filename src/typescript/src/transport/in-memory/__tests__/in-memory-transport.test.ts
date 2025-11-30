import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import { TestEnvironment } from './test-environment';
import { AlphaCommand } from './alpha-command';
import { AlphaEvent } from './alpha-event';
import { PolyBusNotStartedError } from '../../poly-bus-not-started-error';

describe('InMemoryTransport', () => {
  let testEnvironment: TestEnvironment;

  beforeEach(async () => {
    testEnvironment = new TestEnvironment();
    await testEnvironment.setup();
  });

  afterEach(async () => {
    await testEnvironment.stop();
  });

  it('Send_BeforeStarting', async () => {
    // Arrange
    const transaction = await testEnvironment.beta.bus.createOutgoingTransaction();
    let messageReceived = false;
    testEnvironment.alpha.onMessageReceived = async () => {
      // This should not be called
      messageReceived = true;
    };

    // Act
    const command = new AlphaCommand();
    command.name = 'Test';
    transaction.add(command);

    // Assert - should throw an error because the transport is not started
    await expect(transaction.commit()).rejects.toThrow(PolyBusNotStartedError);
    expect(messageReceived).toBe(false);
  });

  it('Send_AfterStarted', async () => {
    // Arrange
    const transaction = await testEnvironment.beta.bus.createOutgoingTransaction();
    const messageReceivedPromise = new Promise<boolean>((resolve) => {
      testEnvironment.alpha.onMessageReceived = async () => {
        resolve(true);
      };
    });

    // Act - send a command from the beta endpoint to alpha endpoint
    await testEnvironment.start();
    const command = new AlphaCommand();
    command.name = 'Test';
    transaction.add(command);
    await transaction.commit();
    const messageReceived = await messageReceivedPromise;

    // Assert
    expect(messageReceived).toBe(true);
  });

  it('Send_WithExplicitEndpoint', async () => {
    // Arrange
    const transaction = await testEnvironment.alpha.bus.createOutgoingTransaction();
    let alphaReceived = false;
    let deadLetterReceived = false;
    const deadLetterPromise = new Promise<string>((resolve) => {
      testEnvironment.alpha.onMessageReceived = async () => {
        // This should NOT be called
        alphaReceived = true;
      };
      testEnvironment.alpha.transport.deadLetterHandler = () => {
        // This should be called
        deadLetterReceived = true;
        resolve(testEnvironment.alpha.transport.deadLetterEndpoint);
      };
    });
    const endpoint = testEnvironment.alpha.transport.deadLetterEndpoint;

    // Act - send the alpha command to dead letter endpoint
    await testEnvironment.start();
    const command = new AlphaCommand();
    command.name = 'Test';
    transaction.add(command, endpoint);
    await transaction.commit();
    const actualEndpoint = await deadLetterPromise;

    // Assert
    expect(actualEndpoint).toBe(endpoint);
    expect(alphaReceived).toBe(false);
    expect(deadLetterReceived).toBe(true);
  });

  it('Send_WithHeaders', async () => {
    // Arrange
    const headerKey = 'X-Custom-Header';
    const headerValue = 'HeaderValue';
    const transaction = await testEnvironment.alpha.bus.createOutgoingTransaction();
    const headerPromise = new Promise<string>((resolve) => {
      testEnvironment.alpha.onMessageReceived = async (incomingTransaction) => {
        const value = incomingTransaction.incomingMessage.headers.get(headerKey) ?? '';
        resolve(value);
      };
    });

    // Act - send a command with a custom header
    await testEnvironment.start();
    const command = new AlphaCommand();
    command.name = 'Test';
    const message = transaction.add(command);
    message.headers.set(headerKey, headerValue);
    await transaction.commit();
    const actualHeaderValue = await headerPromise;

    // Assert
    expect(actualHeaderValue).toBe(headerValue);
  });

  it('Send_WithDelay', async () => {
    // Arrange
    const delay = 5000; // 5 seconds
    const transaction = await testEnvironment.alpha.bus.createOutgoingTransaction();
    const startTime = Date.now();
    const elapsedPromise = new Promise<number>((resolve) => {
      testEnvironment.alpha.onMessageReceived = async () => {
        const elapsed = Date.now() - startTime;
        resolve(elapsed);
      };
    });

    // Act - send message with delay
    await testEnvironment.start();
    const command = new AlphaCommand();
    command.name = 'Test';
    const message = transaction.add(command);
    message.deliverAt = new Date(Date.now() + delay);
    await transaction.commit();
    const elapsed = await elapsedPromise;

    // Assert
    expect(elapsed).toBeGreaterThanOrEqual(delay - 1000); // allow 1 second of leeway
    expect(elapsed).toBeLessThanOrEqual(delay + 1000); // allow 1 second of leeway
  }, 10000); // 10 second timeout for this test

  it('Send_WithExpiredDelay', async () => {
    // Arrange
    const transaction = await testEnvironment.alpha.bus.createOutgoingTransaction();
    const messageReceivedPromise = new Promise<boolean>((resolve) => {
      testEnvironment.alpha.onMessageReceived = async () => {
        resolve(true);
      };
    });

    // Act - schedule command to be delivered in the past
    await testEnvironment.start();
    const command = new AlphaCommand();
    command.name = 'Test';
    const message = transaction.add(command);
    message.deliverAt = new Date(Date.now() - 1000); // 1 second in the past
    await transaction.commit();
    const messageReceived = await messageReceivedPromise;

    // Assert
    expect(messageReceived).toBe(true);
  });

  it('Start_WhenAlreadyStarted', async () => {
    // Act
    await testEnvironment.start();

    // Assert - starting again should not throw an error
    await expect(testEnvironment.start()).resolves.not.toThrow();
  });

  it('Subscribe_BeforeStarted', async () => {
    // Arrange
    const transaction = await testEnvironment.alpha.bus.createOutgoingTransaction();
    let messageReceived = false;
    testEnvironment.beta.onMessageReceived = async () => {
      messageReceived = true;
    };

    // Act - subscribing before starting should throw an error
    await expect(
      testEnvironment.beta.transport.subscribe(
        testEnvironment.beta.bus.messages.getMessageInfo(AlphaEvent)!
      )
    ).rejects.toThrow(PolyBusNotStartedError);

    const event = new AlphaEvent();
    event.name = 'Test';
    transaction.add(event);

    await expect(transaction.commit()).rejects.toThrow(PolyBusNotStartedError);

    // Assert
    expect(messageReceived).toBe(false);
  });

  it('Subscribe', async () => {
    // Arrange
    const transaction = await testEnvironment.alpha.bus.createOutgoingTransaction();
    const messageReceivedPromise = new Promise<boolean>((resolve) => {
      testEnvironment.beta.onMessageReceived = async () => {
        resolve(true);
      };
    });
    await testEnvironment.start();

    // Act - subscribe and send event
    await testEnvironment.beta.transport.subscribe(
      testEnvironment.beta.bus.messages.getMessageInfo(AlphaEvent)!
    );
    const event = new AlphaEvent();
    event.name = 'Test';
    transaction.add(event);
    await transaction.commit();
    const messageReceived = await messageReceivedPromise;

    // Assert
    expect(messageReceived).toBe(true);
  });
});
