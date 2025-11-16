import { describe, it, expect, beforeEach, jest } from '@jest/globals';
import { Headers } from '../../../../../../headers';
import { IncomingMessage } from '../../../incoming-message';
import { IncomingTransaction } from '../../../../incoming-transaction';
import { IPolyBus } from '../../../../../../i-poly-bus';
import { JsonHandlers } from '../json-handlers';
import { messageInfo } from '../../../message-info';
import { Messages } from '../../../messages';
import { MessageType } from '../../../message-info';
import { OutgoingTransaction } from '../../../../outgoing-transaction';

/**
 * Jest tests for JsonHandlers serialization and deserialization functionality.
 *
 * These tests are based on the C# NUnit tests for the JsonHandlers class,
 * adapted for TypeScript and Jest testing framework. The tests cover:
 *
 * - Deserializer functionality with valid/invalid type headers
 * - Custom JSON reviver functions
 * - Error handling for missing/invalid types
 * - Serializer functionality with message type headers
 * - Custom JSON replacer functions and content types
 * - Multiple message handling
 * - Configuration properties and defaults
 */

/**
 * Test class for JsonHandlers serialization and deserialization
 */
describe('JsonHandlers', () => {
  let jsonHandlers: JsonHandlers;
  let mockBus: jest.Mocked<IPolyBus>;
  let messages: Messages;

  beforeEach(() => {
    jsonHandlers = new JsonHandlers();
    messages = new Messages();

    mockBus = {
      transport: {} as any,
      incomingHandlers: [],
      outgoingHandlers: [],
      messages: messages,
      name: 'MockBus',
      createTransaction: jest.fn(),
      send: jest.fn(),
      start: jest.fn(),
      stop: jest.fn()
    } as any;
  });

  describe('Deserializer Tests', () => {
    it('should deserialize message with valid type header', async () => {
      // Arrange
      const testMessage = { id: 1, name: 'Test' };
      const serializedBody = JSON.stringify(testMessage);

      @messageInfo(MessageType.Command, 'test-service', 'TestMessage', 1, 0, 0)
      class TestMessage {
        public id: number = 0;
        public name: string = '';
      }

      messages.add(TestMessage);
      const header = 'endpoint=test-service, type=Command, name=TestMessage, version=1.0.0';

      const incomingMessage = new IncomingMessage(mockBus, serializedBody);
      incomingMessage.headers.set(Headers.MessageType, header);

      const transaction = new MockIncomingTransaction(mockBus, incomingMessage);

      let nextCalled = false;
      const next = async () => { nextCalled = true; };

      // Act
      await jsonHandlers.deserializer(transaction, next);

      // Assert
      expect(nextCalled).toBe(true);
      expect(incomingMessage.message).not.toBeNull();
      expect(incomingMessage.message).toEqual(testMessage);
    });

    it('should deserialize message with custom JSON reviver', async () => {
      // Arrange
      const jsonHandlers = new JsonHandlers();
      jsonHandlers.jsonReviver = (key: string, value: any) => {
        if (key === 'name' && typeof value === 'string') {
          return value.toUpperCase();
        }
        return value;
      };

      const testMessage = { id: 2, name: 'test' };
      const serializedBody = JSON.stringify(testMessage);

      @messageInfo(MessageType.Command, 'test-service', 'TestMessage', 1, 0, 0)
      class TestMessage {
        public id: number = 0;
        public name: string = '';
      }

      messages.add(TestMessage);
      const header = 'endpoint=test-service, type=Command, name=TestMessage, version=1.0.0';

      const incomingMessage = new IncomingMessage(mockBus, serializedBody);
      incomingMessage.headers.set(Headers.MessageType, header);

      const transaction = new MockIncomingTransaction(mockBus, incomingMessage);

      let nextCalled = false;
      const next = async () => { nextCalled = true; };

      // Act
      await jsonHandlers.deserializer(transaction, next);

      // Assert
      expect(nextCalled).toBe(true);
      expect(incomingMessage.message).toEqual({ id: 2, name: 'TEST' });
    });

    it('should parse as generic object when type is unknown and throwOnMissingType is false', async () => {
      // Arrange
      const jsonHandlers = new JsonHandlers();
      jsonHandlers.throwOnMissingType = false;

      const testObject = { id: 3, name: 'Unknown' };
      const serializedBody = JSON.stringify(testObject);
      const header = 'endpoint=test-service, type=Command, name=UnknownMessage, version=1.0.0';

      const incomingMessage = new IncomingMessage(mockBus, serializedBody);
      incomingMessage.headers.set(Headers.MessageType, header);

      const transaction = new MockIncomingTransaction(mockBus, incomingMessage);

      let nextCalled = false;
      const next = async () => { nextCalled = true; };

      // Act
      await jsonHandlers.deserializer(transaction, next);

      // Assert
      expect(nextCalled).toBe(true);
      expect(incomingMessage.message).not.toBeNull();
      expect(incomingMessage.message).toEqual(testObject);
    });

    it('should throw exception when type is unknown and throwOnMissingType is true', async () => {
      // Arrange
      const jsonHandlers = new JsonHandlers();
      jsonHandlers.throwOnMissingType = true;

      const testObject = { id: 4, name: 'Error' };
      const serializedBody = JSON.stringify(testObject);
      const header = 'endpoint=test-service, type=Command, name=UnknownMessage, version=1.0.0';

      const incomingMessage = new IncomingMessage(mockBus, serializedBody);
      incomingMessage.headers.set(Headers.MessageType, header);

      const transaction = new MockIncomingTransaction(mockBus, incomingMessage);

      const next = async () => {};

      // Act & Assert
      await expect(jsonHandlers.deserializer(transaction, next))
        .rejects.toThrow('The type header is missing, invalid, or if the type cannot be found.');
    });

    it('should throw exception when type header is missing and throwOnMissingType is true', async () => {
      // Arrange
      const jsonHandlers = new JsonHandlers();
      jsonHandlers.throwOnMissingType = true;

      const incomingMessage = new IncomingMessage(mockBus, '{}');
      const transaction = new MockIncomingTransaction(mockBus, incomingMessage);

      const next = async () => {};

      // Act & Assert
      await expect(jsonHandlers.deserializer(transaction, next))
        .rejects.toThrow('The type header is missing, invalid, or if the type cannot be found.');
    });

    it('should throw error when JSON is invalid', async () => {
      // Arrange
      @messageInfo(MessageType.Command, 'test-service', 'TestMessage', 1, 0, 0)
      class TestMessage {
        public id: number = 0;
        public name: string = '';
      }

      messages.add(TestMessage);
      const header = 'endpoint=test-service, type=Command, name=TestMessage, version=1.0.0';

      const incomingMessage = new IncomingMessage(mockBus, 'invalid json');
      incomingMessage.headers.set(Headers.MessageType, header);

      const transaction = new MockIncomingTransaction(mockBus, incomingMessage);

      const next = async () => {};

      // Act & Assert
      await expect(jsonHandlers.deserializer(transaction, next))
        .rejects.toThrow('Failed to parse JSON message body:');
    });
  });

  describe('Serializer Tests', () => {
    it('should serialize message and set headers', async () => {
      // Arrange
      @messageInfo(MessageType.Command, 'test-service', 'TestMessage', 1, 0, 0)
      class TestMessage {
        public id: number;
        public name: string;

        constructor(id: number, name: string) {
          this.id = id;
          this.name = name;
        }
      }

      const testMessage = new TestMessage(5, 'Serialize');
      messages.add(TestMessage);

      const mockTransaction = new MockOutgoingTransaction(mockBus);
      const outgoingMessage = mockTransaction.addOutgoingMessage(testMessage);

      let nextCalled = false;
      const next = async () => { nextCalled = true; };

      // Act
      await jsonHandlers.serializer(mockTransaction, next);

      // Assert
      expect(nextCalled).toBe(true);
      expect(outgoingMessage.body).not.toBeNull();

      const deserializedMessage = JSON.parse(outgoingMessage.body);
      expect(deserializedMessage.id).toBe(5);
      expect(deserializedMessage.name).toBe('Serialize');

      expect(outgoingMessage.headers.get(Headers.ContentType)).toBe('application/json');
      expect(outgoingMessage.headers.get(Headers.MessageType)).toBe('endpoint=test-service, type=command, name=TestMessage, version=1.0.0');
    });

    it('should use custom content type when specified', async () => {
      // Arrange
      const customContentType = 'application/custom-json';
      const jsonHandlers = new JsonHandlers();
      jsonHandlers.contentType = customContentType;
      jsonHandlers.throwOnInvalidType = false;

      @messageInfo(MessageType.Command, 'test-service', 'TestMessage', 1, 0, 0)
      class TestMessage {
        public id: number;
        public name: string;

        constructor(id: number, name: string) {
          this.id = id;
          this.name = name;
        }
      }

      const testMessage = new TestMessage(6, 'Custom');
      messages.add(TestMessage);

      const mockTransaction = new MockOutgoingTransaction(mockBus);
      const outgoingMessage = mockTransaction.addOutgoingMessage(testMessage);

      let nextCalled = false;
      const next = async () => { nextCalled = true; };

      // Act
      await jsonHandlers.serializer(mockTransaction, next);

      // Assert
      expect(nextCalled).toBe(true);
      expect(outgoingMessage.headers.get(Headers.ContentType)).toBe(customContentType);
    });

    it('should serialize with custom JSON replacer', async () => {
      // Arrange
      const jsonHandlers = new JsonHandlers();
      jsonHandlers.jsonReplacer = (key: string, value: any) => {
        if (key === 'name' && typeof value === 'string') {
          return value.toLowerCase();
        }
        return value;
      };
      jsonHandlers.throwOnInvalidType = false;

      @messageInfo(MessageType.Command, 'test-service', 'TestMessage', 1, 0, 0)
      class TestMessage {
        public id: number;
        public name: string;

        constructor(id: number, name: string) {
          this.id = id;
          this.name = name;
        }
      }

      const testMessage = new TestMessage(7, 'OPTIONS');
      messages.add(TestMessage);

      const mockTransaction = new MockOutgoingTransaction(mockBus);
      const outgoingMessage = mockTransaction.addOutgoingMessage(testMessage);

      let nextCalled = false;
      const next = async () => { nextCalled = true; };

      // Act
      await jsonHandlers.serializer(mockTransaction, next);

      // Assert
      expect(nextCalled).toBe(true);
      expect(outgoingMessage.body).toContain('"name":"options"');
    });

    it('should skip header setting when type is unknown and throwOnInvalidType is false', async () => {
      // Arrange
      const jsonHandlers = new JsonHandlers();
      jsonHandlers.throwOnInvalidType = false;

      class UnknownMessage {
        public data: string;

        constructor(data: string) {
          this.data = data;
        }
      }

      const testMessage = new UnknownMessage('test');

      const mockTransaction = new MockOutgoingTransaction(mockBus);
      const outgoingMessage = mockTransaction.addOutgoingMessage(testMessage, 'unknown-endpoint');

      let nextCalled = false;
      const next = async () => { nextCalled = true; };

      // Act
      await jsonHandlers.serializer(mockTransaction, next);

      // Assert
      expect(nextCalled).toBe(true);
      expect(outgoingMessage.body).not.toBeNull();
      expect(outgoingMessage.headers.get(Headers.ContentType)).toBe('application/json');
      expect(outgoingMessage.headers.has(Headers.MessageType)).toBe(false);
    });

    it('should throw exception when type is unknown and throwOnInvalidType is true', async () => {
      // Arrange
      const jsonHandlers = new JsonHandlers();
      jsonHandlers.throwOnInvalidType = true;

      class UnknownMessage {
        public data: string;

        constructor(data: string) {
          this.data = data;
        }
      }

      const testMessage = new UnknownMessage('error');

      const mockTransaction = new MockOutgoingTransaction(mockBus);
      mockTransaction.addOutgoingMessage(testMessage, 'unknown-endpoint');

      const next = async () => {};

      // Act & Assert
      await expect(jsonHandlers.serializer(mockTransaction, next))
        .rejects.toThrow('The header has an invalid type.');
    });

    it('should serialize multiple messages', async () => {
      // Arrange
      @messageInfo(MessageType.Command, 'test-service', 'TestMessage', 1, 0, 0)
      class TestMessage {
        public id: number;
        public name: string;

        constructor(id: number, name: string) {
          this.id = id;
          this.name = name;
        }
      }

      const testMessage1 = new TestMessage(8, 'First');
      const testMessage2 = new TestMessage(9, 'Second');

      messages.add(TestMessage);

      const mockTransaction = new MockOutgoingTransaction(mockBus);
      const outgoingMessage1 = mockTransaction.addOutgoingMessage(testMessage1);
      const outgoingMessage2 = mockTransaction.addOutgoingMessage(testMessage2);

      let nextCalled = false;
      const next = async () => { nextCalled = true; };

      // Act
      await jsonHandlers.serializer(mockTransaction, next);

      // Assert
      expect(nextCalled).toBe(true);
      expect(outgoingMessage1.body).not.toBeNull();
      expect(outgoingMessage2.body).not.toBeNull();

      const deserializedMessage1 = JSON.parse(outgoingMessage1.body);
      const deserializedMessage2 = JSON.parse(outgoingMessage2.body);

      expect(deserializedMessage1.id).toBe(8);
      expect(deserializedMessage1.name).toBe('First');
      expect(deserializedMessage2.id).toBe(9);
      expect(deserializedMessage2.name).toBe('Second');
    });

    it('should call next when no outgoing messages exist', async () => {
      // Arrange
      const mockTransaction = new MockOutgoingTransaction(mockBus);

      let nextCalled = false;
      const next = async () => { nextCalled = true; };

      // Act
      await jsonHandlers.serializer(mockTransaction, next);

      // Assert
      expect(nextCalled).toBe(true);
    });
  });

  describe('Configuration Properties', () => {
    it('should have default content type as application/json', () => {
      const handlers = new JsonHandlers();
      expect(handlers.contentType).toBe('application/json');
    });

    it('should have default throwOnMissingType as true', () => {
      const handlers = new JsonHandlers();
      expect(handlers.throwOnMissingType).toBe(true);
    });

    it('should have default throwOnInvalidType as true', () => {
      const handlers = new JsonHandlers();
      expect(handlers.throwOnInvalidType).toBe(true);
    });

    it('should allow custom configuration', () => {
      const handlers = new JsonHandlers();
      handlers.contentType = 'custom/type';
      handlers.throwOnMissingType = false;
      handlers.throwOnInvalidType = false;
      handlers.jsonReplacer = (_key, value) => value;
      handlers.jsonReviver = (_key, value) => value;

      expect(handlers.contentType).toBe('custom/type');
      expect(handlers.throwOnMissingType).toBe(false);
      expect(handlers.throwOnInvalidType).toBe(false);
      expect(handlers.jsonReplacer).toBeDefined();
      expect(handlers.jsonReviver).toBeDefined();
    });
  });
});

// Mock classes to support the tests
class MockIncomingTransaction extends IncomingTransaction {
  constructor(bus: IPolyBus, incomingMessage: IncomingMessage) {
    super(bus, incomingMessage);
  }

  public override async abort(): Promise<void> {
    // Mock implementation
  }

  public override async commit(): Promise<void> {
    // Mock implementation
  }
}

class MockOutgoingTransaction extends OutgoingTransaction {
  constructor(bus: IPolyBus) {
    super(bus);
  }

  public override async abort(): Promise<void> {
    // Mock implementation
  }

  public override async commit(): Promise<void> {
    // Mock implementation
  }
}
