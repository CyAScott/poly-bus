import { MessageInfo } from './message-info';

/**
 * Interface for storing message type and metadata information
 */
interface MessageEntry {
  attribute: MessageInfo;
  header: string;
}

/**
 * A collection of message types and their associated message headers.
 */
export class Messages {
  private readonly _map = new Map<string, Function | null>();
  private readonly _types = new Map<Function, MessageEntry>();

  /**
   * Gets the message attribute associated with the specified type.
   */
  public getMessageInfo(type: Function): MessageInfo | null {
    const entry = this._types.get(type);
    return entry ? entry.attribute : null;
  }

  /**
   * Attempts to get the message type (constructor function) associated with the specified header.
   * @param header The message header string to look up
   * @returns If found, returns the message constructor function; otherwise, returns null.
   */
  public getTypeByHeader(header: string): Function | null {
    const attribute = MessageInfo.getAttributeFromHeader(header);
    if (!attribute) {
      return null;
    }

    // Check if we already have this header cached
    if (this._map.has(header)) {
      return this._map.get(header) || null;
    }

    // Find the type that matches this attribute
    for (const [type, entry] of this._types.entries()) {
      if (entry.attribute.equals(attribute)) {
        this._map.set(header, type);
        return type;
      }
    }

    // Not found, cache null result
    this._map.set(header, null);
    return null;
  }

  /**
   * Attempts to get the message header associated with the specified type.
   * @param type The message constructor function to look up
   * @returns If found, returns the message header; otherwise, returns null.
   */
  public getHeader(type: Function): string | null {
    const entry = this._types.get(type);
    return entry ? entry.header : null;
  }

  /**
   * Adds a message type to the collection.
   * The message type must have MessageInfo metadata defined via the @messageInfo decorator.
   * @param messageType The message constructor function to add
   * @returns The MessageInfo associated with the message type.
   * @throws Error if the type does not have MessageInfo metadata
   * @throws Error if the type has already been added
   */
  public add(messageType: Function): MessageInfo {
    if (this._types.has(messageType)) {
      throw new Error(`Type ${messageType.name} has already been added to the Messages collection.`);
    }

    const attribute = MessageInfo.getMetadata(messageType);
    if (!attribute) {
      throw new Error(`Type ${messageType.name} does not have MessageInfo metadata. Make sure to use the @messageInfo decorator.`);
    }

    const header = attribute.toString(true);
    const entry: MessageEntry = { attribute, header };

    this._types.set(messageType, entry);
    this._map.set(header, messageType);

    return attribute;
  }

  /**
   * Attempts to get the message type associated with the specified MessageInfo.
   * @param messageInfo The MessageInfo to look up
   * @returns If found, returns the message constructor function; otherwise, returns null.
   */
  public getTypeByMessageInfo(messageInfo: MessageInfo): Function | null {
    for (const [type, entry] of this._types.entries()) {
      if (entry.attribute.equals(messageInfo)) {
        return type;
      }
    }
    return null;
  }
}
