import { MessageInfo } from './message-info';
import { PolyBusMessageNotFoundError } from './poly-bus-message-not-found-error';

/**
 * Interface for storing message type and metadata information
 */
interface MessageEntry {
  attribute: MessageInfo;
  header: string;
}

/**
 * A collection of message types and their associated message headers and attributes.
 */
export class Messages {
  protected types: Map<Function, MessageEntry> = new Map<Function, MessageEntry>();

  /**
   * Gets the message attribute associated with the specified type.
   * @returns The MessageInfo associated with the specified type.
   * @throws PolyBusMessageNotFoundError If no message attribute is found for the specified type.
   */
  public getMessageInfo(type: Function): MessageInfo {
    const entry = this.types.get(type);
    if (!entry) {
      throw new PolyBusMessageNotFoundError();
    }
    return entry.attribute;
  }

  /**
   * Gets the message header associated with the specified attribute.
   * @returns The message header associated with the specified attribute.
   * @throws PolyBusMessageNotFoundError If no message header is found for the specified attribute.
   */
  public getHeaderByMessageInfo(messageInfo: MessageInfo): string {
    for (const entry of this.types.values()) {
      if (entry.attribute.equals(messageInfo)) {
        return messageInfo.toString(true);
      }
    }
    throw new PolyBusMessageNotFoundError();
  }

  /**
   * Adds a message type to the collection.
   * The message type must have MessageInfo metadata defined via the @messageInfo decorator.
   * @param messageType The message constructor function to add
   * @returns The MessageInfo associated with the message type.
   * @throws PolyBusMessageNotFoundError If the message type does not have a message info attribute defined.
   * @throws PolyBusMessageNotFoundError If the type has already been added.
   */
  public add(messageType: Function): MessageInfo {
    const attribute = MessageInfo.getMetadata(messageType);
    if (!attribute) {
      throw new PolyBusMessageNotFoundError();
    }

    const header = attribute.toString(true);
    const entry: MessageEntry = { attribute, header };

    if (this.types.has(messageType)) {
      throw new PolyBusMessageNotFoundError();
    }

    this.types.set(messageType, entry);

    return attribute;
  }

  /**
   * Attempts to get the message type associated with the specified attribute.
   * @param messageInfo The MessageInfo to look up
   * @returns The message type associated with the specified attribute.
   * @throws PolyBusMessageNotFoundError If no message type is found for the specified message info attribute.
   */
  public getTypeByMessageInfo(messageInfo: MessageInfo): Function {
    for (const [type, entry] of this.types.entries()) {
      if (entry.attribute.equals(messageInfo)) {
        return type;
      }
    }
    throw new PolyBusMessageNotFoundError();
  }
}
