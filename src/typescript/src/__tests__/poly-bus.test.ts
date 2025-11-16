import { describe, it, expect, beforeEach } from '@jest/globals';
import { PolyBusBuilder } from '../poly-bus-builder';
import { IncomingTransaction } from '../transport/transaction/incoming-transaction';
import { OutgoingTransaction } from '../transport/transaction/outgoing-transaction';
import { InMemoryTransport } from '../transport/in-memory/in-memory-transport';

describe('PolyBus', () => {
  let inMemoryTransport: InMemoryTransport;

  beforeEach(() => {
    inMemoryTransport = new InMemoryTransport();
  });

  describe('IncomingHandlers', () => {
    it('should invoke incoming handlers', async () => {
      // Arrange
      const incomingTransactionPromise = new Promise<IncomingTransaction>((resolve) => {
        const builder = new PolyBusBuilder();
        builder.incomingHandlers.push(async (transaction, next) => {
          await next();
          resolve(transaction);
        });
        builder.transportFactory = async (builder, bus) => inMemoryTransport.addEndpoint(builder, bus);

        builder.build().then(async (bus) => {
          // Act
          await bus.start();
          const outgoingTransaction = await bus.createTransaction();
          outgoingTransaction.addOutgoingMessage('Hello world', 'unknown-endpoint');
          await outgoingTransaction.commit();

          // Allow processing to complete
          // eslint-disable-next-line no-undef
          await new Promise(resolve => setTimeout(resolve, 10));
          await bus.stop();
        });
      });

      const transaction = await incomingTransactionPromise;

      // Assert
      expect(transaction).toBeDefined();
      expect(transaction.incomingMessage.body).toBe('Hello world');
    });

    it('should invoke incoming handlers even when exception is thrown', async () => {
      // Arrange
      const incomingTransactionPromise = new Promise<IncomingTransaction>((resolve) => {
        const builder = new PolyBusBuilder();
        builder.incomingHandlers.push(async (transaction) => {
          resolve(transaction);
          throw new Error(transaction.incomingMessage.body);
        });
        builder.transportFactory = async (builder, bus) => inMemoryTransport.addEndpoint(builder, bus);

        builder.build().then(async (bus) => {
          // Act
          await bus.start();
          const outgoingTransaction = await bus.createTransaction();
          outgoingTransaction.addOutgoingMessage('Hello world', 'unknown-endpoint');
          await outgoingTransaction.commit();

          // Allow processing to complete
          // eslint-disable-next-line no-undef
          await new Promise(resolve => setTimeout(resolve, 10));
          await bus.stop();
        });
      });

      const transaction = await incomingTransactionPromise;

      // Assert
      expect(transaction).toBeDefined();
      expect(transaction.incomingMessage.body).toBe('Hello world');
    });

    it('should invoke incoming handlers with delay', async () => {
      // Arrange
      const processedOnPromise = new Promise<Date>((resolve) => {
        const builder = new PolyBusBuilder();
        builder.incomingHandlers.push(async (_, next) => {
          await next();
          resolve(new Date());
        });
        builder.transportFactory = async (builder, bus) => inMemoryTransport.addEndpoint(builder, bus);

        builder.build().then(async (bus) => {
          // Act
          await bus.start();
          const outgoingTransaction = await bus.createTransaction();
          const message = outgoingTransaction.addOutgoingMessage('Hello world', 'unknown-endpoint');
          const scheduledAt = new Date(Date.now() + 1000); // 1 second from now
          message.deliverAt = scheduledAt;
          await outgoingTransaction.commit();

          // Allow processing to complete
          // eslint-disable-next-line no-undef
          setTimeout(async () => {
            await bus.stop();
          }, 2000); // Stop after 2 seconds
        });
      });

      const processedOn = await processedOnPromise;

      // Assert
      expect(processedOn).toBeDefined();
      const now = new Date();
      const timeDiff = processedOn.getTime() - (now.getTime() - 2000); // Approximately when it was scheduled
      expect(timeDiff).toBeGreaterThanOrEqual(800); // Allow some margin for timing
    }, 5000); // 5 second timeout for this test

    it('should invoke incoming handlers with delay and exception', async () => {
      // Arrange
      const processedOnPromise = new Promise<Date>((resolve) => {
        const builder = new PolyBusBuilder();
        builder.incomingHandlers.push(async (transaction) => {
          resolve(new Date());
          throw new Error(transaction.incomingMessage.body);
        });
        builder.transportFactory = async (builder, bus) => inMemoryTransport.addEndpoint(builder, bus);

        builder.build().then(async (bus) => {
          // Act
          await bus.start();
          const outgoingTransaction = await bus.createTransaction();
          const message = outgoingTransaction.addOutgoingMessage('Hello world', 'unknown-endpoint');
          const scheduledAt = new Date(Date.now() + 1000); // 1 second from now
          message.deliverAt = scheduledAt;
          await outgoingTransaction.commit();

          // Allow processing to complete
          // eslint-disable-next-line no-undef
          setTimeout(async () => {
            await bus.stop();
          }, 2000); // Stop after 2 seconds
        });
      });

      const processedOn = await processedOnPromise;

      // Assert
      expect(processedOn).toBeDefined();
      const now = new Date();
      const timeDiff = processedOn.getTime() - (now.getTime() - 2000); // Approximately when it was scheduled
      expect(timeDiff).toBeGreaterThanOrEqual(800); // Allow some margin for timing
    }, 5000); // 5 second timeout for this test
  });

  describe('OutgoingHandlers', () => {
    it('should invoke outgoing handlers', async () => {
      // Arrange
      const outgoingTransactionPromise = new Promise<OutgoingTransaction>((resolve) => {
        const builder = new PolyBusBuilder();
        builder.outgoingHandlers.push(async (transaction, next) => {
          await next();
          resolve(transaction);
        });
        builder.transportFactory = async (builder, bus) => inMemoryTransport.addEndpoint(builder, bus);

        builder.build().then(async (bus) => {
          // Act
          await bus.start();
          const outgoingTransaction = await bus.createTransaction();
          outgoingTransaction.addOutgoingMessage('Hello world', 'unknown-endpoint');
          await outgoingTransaction.commit();

          // Allow processing to complete
          // eslint-disable-next-line no-undef
          await new Promise(resolve => setTimeout(resolve, 10));
          await bus.stop();
        });
      });

      const transaction = await outgoingTransactionPromise;

      // Assert
      expect(transaction).toBeDefined();
      expect(transaction.outgoingMessages).toHaveLength(1);
      expect(transaction.outgoingMessages[0].body).toBe('Hello world');
    });

    it('should invoke outgoing handlers and handle exceptions', async () => {
      // Arrange
      const builder = new PolyBusBuilder();
      builder.outgoingHandlers.push(async (transaction) => {
        throw new Error(transaction.outgoingMessages[0].body);
      });
      builder.transportFactory = async (builder, bus) => inMemoryTransport.addEndpoint(builder, bus);

      const bus = await builder.build();

      // Act & Assert
      await bus.start();
      const outgoingTransaction = await bus.createTransaction();
      outgoingTransaction.addOutgoingMessage('Hello world', 'unknown-endpoint');

      await expect(outgoingTransaction.commit()).rejects.toThrow('Hello world');

      await bus.stop();
    });
  });
});
