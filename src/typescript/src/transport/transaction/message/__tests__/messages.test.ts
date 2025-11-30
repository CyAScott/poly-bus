import { describe, it, expect, beforeEach } from '@jest/globals';
import { Messages } from '../messages';
import { MessageInfo, messageInfo } from '../message-info';
import { MessageType } from '../message-type';
import { PolyBusMessageNotFoundError } from '../poly-bus-message-not-found-error';

describe('Messages', () => {
  let messages: Messages;

  beforeEach(() => {
    messages = new Messages();
  });

  // Test Message Classes
  @messageInfo(MessageType.Command, 'polybus', 'polybus-command', 1, 0, 0)
  class Command {
    // Empty class for testing
  }

  @messageInfo(MessageType.Event, 'polybus', 'polybus-event', 2, 1, 3)
  class Event {
    // Empty class for testing
  }

  class MessageWithoutAttribute {
    // Empty class without decorator
  }

  describe('Add', () => {
    it('Add_ValidMessageType_ReturnsMessageInfo', () => {
      // Act
      const result = messages.add(Command);

      // Assert
      expect(result).not.toBeNull();
      expect(result.type).toBe(MessageType.Command);
      expect(result.endpoint).toBe('polybus');
      expect(result.name).toBe('polybus-command');
      expect(result.major).toBe(1);
      expect(result.minor).toBe(0);
      expect(result.patch).toBe(0);
    });

    it('Add_MessageTypeWithoutAttribute_ThrowsError', () => {
      // Act & Assert
      expect(() => messages.add(MessageWithoutAttribute)).toThrow(PolyBusMessageNotFoundError);
    });

    it('Add_SameTypeTwice_ThrowsError', () => {
      // Arrange
      messages.add(Command);

      // Act & Assert
      expect(() => messages.add(Command)).toThrow(PolyBusMessageNotFoundError);
    });
  });

  describe('GetMessageInfo', () => {
    it('GetMessageInfo_ExistingType_ReturnsCorrectMessageInfo', () => {
      // Arrange
      messages.add(Command);

      // Act
      const result = messages.getMessageInfo(Command);

      // Assert
      expect(result).not.toBeNull();
      expect(result.type).toBe(MessageType.Command);
      expect(result.endpoint).toBe('polybus');
      expect(result.name).toBe('polybus-command');
    });

    it('GetMessageInfo_NonExistentType_ThrowsError', () => {
      // Act & Assert
      expect(() => messages.getMessageInfo(Command)).toThrow(PolyBusMessageNotFoundError);
    });
  });

  describe('GetTypeByMessageInfo', () => {
    it('GetTypeByMessageInfo_ExistingMessageInfo_ReturnsCorrectType', () => {
      // Arrange
      messages.add(Event);
      const messageInfo = new MessageInfo(MessageType.Event, 'polybus', 'polybus-event', 2, 1, 3);

      // Act
      const result = messages.getTypeByMessageInfo(messageInfo);

      // Assert
      expect(result).toBe(Event);
    });

    it('GetTypeByMessageInfo_NonExistentMessageInfo_ThrowsError', () => {
      // Arrange
      const messageInfo = new MessageInfo(MessageType.Command, 'unknown', 'unknown-command', 1, 0, 0);

      // Act & Assert
      expect(() => messages.getTypeByMessageInfo(messageInfo)).toThrow(PolyBusMessageNotFoundError);
    });

    it('GetTypeByMessageInfo_DifferentMinorPatchVersions_ReturnsType', () => {
      // Arrange
      messages.add(Event); // Has version 2.1.3
      const messageInfoDifferentMinor = new MessageInfo(MessageType.Event, 'polybus', 'polybus-event', 2, 5, 3);
      const messageInfoDifferentPatch = new MessageInfo(MessageType.Event, 'polybus', 'polybus-event', 2, 1, 9);

      // Act
      const result1 = messages.getTypeByMessageInfo(messageInfoDifferentMinor);
      const result2 = messages.getTypeByMessageInfo(messageInfoDifferentPatch);

      // Assert
      expect(result1).toBe(Event);
      expect(result2).toBe(Event);
    });

    it('GetTypeByMessageInfo_DifferentMajorVersion_ThrowsError', () => {
      // Arrange
      messages.add(Event); // Has version 2.1.3
      const messageInfoDifferentMajor = new MessageInfo(MessageType.Event, 'polybus', 'polybus-event', 3, 1, 3);

      // Act & Assert
      expect(() => messages.getTypeByMessageInfo(messageInfoDifferentMajor)).toThrow(PolyBusMessageNotFoundError);
    });
  });

  describe('GetHeaderByMessageInfo', () => {
    it('GetHeaderByMessageInfo_ExistingMessageInfo_ReturnsCorrectHeader', () => {
      // Arrange
      messages.add(Command);
      const messageInfo = new MessageInfo(MessageType.Command, 'polybus', 'polybus-command', 1, 0, 0);

      // Act
      const result = messages.getHeaderByMessageInfo(messageInfo);

      // Assert
      expect(result).not.toBeNull();
      expect(result).toBeTruthy();
      expect(result).toBe(messageInfo.toString(true));
    });

    it('GetHeaderByMessageInfo_NonExistentMessageInfo_ThrowsError', () => {
      // Arrange
      const messageInfo = new MessageInfo(MessageType.Command, 'unknown', 'unknown-command', 1, 0, 0);

      // Act & Assert
      expect(() => messages.getHeaderByMessageInfo(messageInfo)).toThrow(PolyBusMessageNotFoundError);
    });

    it('GetHeaderByMessageInfo_DifferentMajorVersion_ThrowsError', () => {
      // Arrange
      messages.add(Event); // Has version 2.1.3
      const messageInfoDifferentMajor = new MessageInfo(MessageType.Event, 'polybus', 'polybus-event', 3, 1, 3);

      // Act & Assert
      expect(() => messages.getHeaderByMessageInfo(messageInfoDifferentMajor)).toThrow(PolyBusMessageNotFoundError);
    });
  });
});
