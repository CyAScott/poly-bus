import { MessageType } from './message-type';

/**
 * Interface to store message metadata on a class constructor
 */
export interface MessageInfoMetadata {
  type: MessageType;
  endpoint: string;
  name: string;
  major: number;
  minor: number;
  patch: number;
}

/**
 * This decorates a message class with metadata about the message.
 * This is used to identify the message type and version so that it can be routed and deserialized appropriately.
 */
export class MessageInfo {
  private static readonly HEADER_PATTERN = /^endpoint\s*=\s*(?<endpoint>[^,\s]+),\s*type\s*=\s*(?<type>[^,\s]+),\s*name\s*=\s*(?<name>[^,\s]+),\s*version\s*=\s*(?<major>\d+)\.(?<minor>\d+)\.(?<patch>\d+)/i;
  private static readonly METADATA_KEY = Symbol('messageInfo');

  constructor(
    public readonly type: MessageType,
    public readonly endpoint: string,
    public readonly name: string,
    public readonly major: number,
    public readonly minor: number,
    public readonly patch: number
  ) {}

  /**
   * Parses a message attribute from a message header string.
   * @param header The header string to parse
   * @returns If the header is valid, returns a MessageInfo instance; otherwise, returns null.
   */
  public static getAttributeFromHeader(header: string): MessageInfo | null {
    const match = this.HEADER_PATTERN.exec(header);

    if (!match || !match.groups) {
      return null;
    }

    const endpoint = match.groups.endpoint;
    const name = match.groups.name;
    const typeStr = match.groups.type.toLowerCase();
    const major = parseInt(match.groups.major, 10);
    const minor = parseInt(match.groups.minor, 10);
    const patch = parseInt(match.groups.patch, 10);

    // Parse MessageType enum
    let type: MessageType;
    if (typeStr === 'command') {
      type = MessageType.Command;
    } else if (typeStr === 'event') {
      type = MessageType.Event;
    } else {
      return null; // Invalid message type
    }

    return new MessageInfo(type, endpoint, name, major, minor, patch);
  }

  /**
   * Gets the MessageInfo metadata from a class constructor
   * @param target The class constructor to get metadata from
   * @returns The MessageInfo instance if found, null otherwise
   */
  public static getMetadata(target: any): MessageInfo | null {
    return Reflect.getMetadata?.(this.METADATA_KEY, target) || target[this.METADATA_KEY] || null;
  }

  /**
   * Compares two message attributes for equality.
   * The patch and minor versions are not considered for equality.
   * @param other The other MessageInfo to compare with
   * @returns True if equal, false otherwise
   */
  public equals(other: MessageInfo | null): boolean {
    return other !== null
      && this.type === other.type
      && this.endpoint === other.endpoint
      && this.name === other.name
      && this.major === other.major;
  }

  /**
   * Serializes the message attribute to a string format suitable for message headers.
   * @param includeVersion Whether to include version information
   * @returns The serialized string
   */
  public toString(includeVersion: boolean = true): string {
    const typeStr = this.type === MessageType.Command ? 'command' : 'event';
    const base = `endpoint=${this.endpoint}, type=${typeStr}, name=${this.name}`;
    return includeVersion ? `${base}, version=${this.major}.${this.minor}.${this.patch}` : base;
  }
}

/**
 * Class decorator factory for attaching MessageInfo metadata to message classes.
 * @param type If the message is a command or event
 * @param endpoint The endpoint that publishes the event message or the endpoint that handles the command
 * @param name The unique name for the message for the given endpoint
 * @param major The major version of the message schema
 * @param minor The minor version of the message schema
 * @param patch The patch version of the message schema
 * @returns Class decorator function
 */
export function messageInfo(
  type: MessageType,
  endpoint: string,
  name: string,
  major: number,
  minor: number,
  patch: number
) {
  return function <T extends new (...args: any[]) => any>(target: T): T {
    const metadata = new MessageInfo(type, endpoint, name, major, minor, patch);

    // Use reflect-metadata if available, otherwise store directly on the constructor
    if (typeof Reflect !== 'undefined' && Reflect.defineMetadata) {
      Reflect.defineMetadata(MessageInfo['METADATA_KEY'], metadata, target);
    } else {
      // Fallback: store directly on the constructor
      (target as any)[MessageInfo['METADATA_KEY']] = metadata;
    }

    return target;
  };
}

// Re-export for convenience
export { MessageType };
