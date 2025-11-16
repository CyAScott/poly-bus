import { describe, it, expect, beforeEach } from '@jest/globals';
import { Messages } from '../messages';
import { MessageInfo, messageInfo } from '../message-info';
import { MessageType } from '../message-type';

describe('Messages', () => {
  let messages: Messages;

  beforeEach(() => {
    messages = new Messages();
  });

  // Test Message Classes
  @messageInfo(MessageType.Command, 'OrderService', 'CreateOrder', 1, 0, 0)
  class CreateOrderCommand {
    public orderId: string = '';
    public amount: number = 0;
  }

  @messageInfo(MessageType.Event, 'OrderService', 'OrderCreated', 2, 1, 3)
  class OrderCreatedEvent {
    public orderId: string = '';
    public createdAt: Date = new Date();
  }

  @messageInfo(MessageType.Command, 'PaymentService', 'ProcessPayment', 1, 5, 2)
  class ProcessPaymentCommand {
    public paymentId: string = '';
    public amount: number = 0;
  }

  class MessageWithoutAttribute {
    public data: string = '';
  }

  describe('add', () => {
    it('should return MessageInfo for valid message type', () => {
      // Act
      const result = messages.add(CreateOrderCommand);

      // Assert
      expect(result).not.toBeNull();
      expect(result.type).toBe(MessageType.Command);
      expect(result.endpoint).toBe('OrderService');
      expect(result.name).toBe('CreateOrder');
      expect(result.major).toBe(1);
      expect(result.minor).toBe(0);
      expect(result.patch).toBe(0);
    });

    it('should throw error for message type without attribute', () => {
      // Act & Assert
      expect(() => messages.add(MessageWithoutAttribute)).toThrow();
      expect(() => messages.add(MessageWithoutAttribute)).toThrow(/does not have MessageInfo metadata/);
      expect(() => messages.add(MessageWithoutAttribute)).toThrow(/MessageWithoutAttribute/);
    });

    it('should throw error when adding same type twice', () => {
      // Arrange
      messages.add(CreateOrderCommand);

      // Act & Assert
      expect(() => messages.add(CreateOrderCommand)).toThrow();
    });
  });

  describe('getMessageInfo', () => {
    it('should return correct MessageInfo for existing type', () => {
      // Arrange
      messages.add(CreateOrderCommand);

      // Act
      const result = messages.getMessageInfo(CreateOrderCommand);

      // Assert
      expect(result).not.toBeNull();
      expect(result!.type).toBe(MessageType.Command);
      expect(result!.endpoint).toBe('OrderService');
      expect(result!.name).toBe('CreateOrder');
    });

    it('should return null for non-existent type', () => {
      // Act
      const result = messages.getMessageInfo(CreateOrderCommand);

      // Assert
      expect(result).toBeNull();
    });
  });

  describe('getHeader', () => {
    it('should return correct header for existing type', () => {
      // Arrange
      messages.add(OrderCreatedEvent);

      // Act
      const result = messages.getHeader(OrderCreatedEvent);

      // Assert
      expect(result).toBe('endpoint=OrderService, type=event, name=OrderCreated, version=2.1.3');
    });

    it('should return null for non-existent type', () => {
      // Act
      const result = messages.getHeader(CreateOrderCommand);

      // Assert
      expect(result).toBeNull();
    });
  });

  describe('getTypeByHeader', () => {
    it('should return correct type for valid header', () => {
      // Arrange
      messages.add(ProcessPaymentCommand);
      const header = 'endpoint=PaymentService, type=Command, name=ProcessPayment, version=1.5.2';

      // Act
      const result = messages.getTypeByHeader(header);

      // Assert
      expect(result).toBe(ProcessPaymentCommand);
    });

    it('should return null for invalid header', () => {
      // Arrange
      const invalidHeader = 'invalid header format';

      // Act
      const result = messages.getTypeByHeader(invalidHeader);

      // Assert
      expect(result).toBeNull();
    });

    it('should return null for non-existent message', () => {
      // Arrange
      const header = 'endpoint=UnknownService, type=Command, name=UnknownCommand, version=1.0.0';

      // Act
      const result = messages.getTypeByHeader(header);

      // Assert
      expect(result).toBeNull();
    });

    it('should cache results', () => {
      // Arrange
      messages.add(CreateOrderCommand);
      const header = 'endpoint=OrderService, type=Command, name=CreateOrder, version=1.0.0';

      // Act
      const result1 = messages.getTypeByHeader(header);
      const result2 = messages.getTypeByHeader(header);

      // Assert
      expect(result1).toBe(CreateOrderCommand);
      expect(result2).toBe(CreateOrderCommand);
      expect(result1).toBe(result2); // Reference equality
    });
  });

  describe('getTypeByMessageInfo', () => {
    it('should return correct type for existing MessageInfo', () => {
      // Arrange
      messages.add(OrderCreatedEvent);
      const messageInfo = new MessageInfo(MessageType.Event, 'OrderService', 'OrderCreated', 2, 1, 3);

      // Act
      const result = messages.getTypeByMessageInfo(messageInfo);

      // Assert
      expect(result).toBe(OrderCreatedEvent);
    });

    it('should return null for non-existent MessageInfo', () => {
      // Arrange
      const messageInfo = new MessageInfo(MessageType.Command, 'UnknownService', 'UnknownCommand', 1, 0, 0);

      // Act
      const result = messages.getTypeByMessageInfo(messageInfo);

      // Assert
      expect(result).toBeNull();
    });

    it('should return type for different minor/patch versions', () => {
      // Arrange
      messages.add(OrderCreatedEvent); // Has version 2.1.3
      const messageInfoDifferentMinor = new MessageInfo(MessageType.Event, 'OrderService', 'OrderCreated', 2, 5, 3);
      const messageInfoDifferentPatch = new MessageInfo(MessageType.Event, 'OrderService', 'OrderCreated', 2, 1, 9);

      // Act
      const result1 = messages.getTypeByMessageInfo(messageInfoDifferentMinor);
      const result2 = messages.getTypeByMessageInfo(messageInfoDifferentPatch);

      // Assert
      expect(result1).toBe(OrderCreatedEvent);
      expect(result2).toBe(OrderCreatedEvent);
    });

    it('should return null for different major version', () => {
      // Arrange
      messages.add(OrderCreatedEvent); // Has version 2.1.3
      const messageInfoDifferentMajor = new MessageInfo(MessageType.Event, 'OrderService', 'OrderCreated', 3, 1, 3);

      // Act
      const result = messages.getTypeByMessageInfo(messageInfoDifferentMajor);

      // Assert
      expect(result).toBeNull();
    });
  });

  describe('multiple messages integration', () => {
    it('should work correctly with multiple messages', () => {
      // Arrange
      messages.add(CreateOrderCommand);
      messages.add(OrderCreatedEvent);
      messages.add(ProcessPaymentCommand);

      // Act & Assert - getMessageInfo
      const commandInfo = messages.getMessageInfo(CreateOrderCommand);
      const eventInfo = messages.getMessageInfo(OrderCreatedEvent);
      const paymentInfo = messages.getMessageInfo(ProcessPaymentCommand);

      expect(commandInfo!.type).toBe(MessageType.Command);
      expect(eventInfo!.type).toBe(MessageType.Event);
      expect(paymentInfo!.endpoint).toBe('PaymentService');

      // Act & Assert - getHeader
      const commandHeader = messages.getHeader(CreateOrderCommand);
      const eventHeader = messages.getHeader(OrderCreatedEvent);

      expect(commandHeader).toContain('OrderService');
      expect(eventHeader).toContain('OrderCreated');

      // Act & Assert - getTypeByHeader
      const typeFromHeader = messages.getTypeByHeader(commandHeader!);
      expect(typeFromHeader).toBe(CreateOrderCommand);
    });
  });
});
