import { Headers } from '../../../../../headers';
import { IncomingTransaction } from '../../../incoming-transaction';
import { OutgoingTransaction } from '../../../outgoing-transaction';

/**
 * JSON serialization and deserialization handlers for PolyBus messages.
 * Uses standard JSON.stringify and JSON.parse methods for processing.
 */
export class JsonHandlers {
  /**
   * Custom JSON replacer function to use during serialization.
   * Equivalent to JsonSerializerOptions in C#.
   */
  public jsonReplacer?: (key: string, value: any) => any;

  /**
   * Custom JSON reviver function to use during deserialization.
   * Equivalent to JsonSerializerOptions in C#.
   */
  public jsonReviver?: (key: string, value: any) => any;

  /**
   * The content type to set on outgoing messages.
   */
  public contentType: string = 'application/json';

  /**
   * If the type header is missing, invalid, or if the type cannot be found, throw an exception.
   */
  public throwOnMissingType: boolean = true;

  /**
   * If the message type is not in the list of known messages, throw an exception.
   */
  public throwOnInvalidType: boolean = true;

  /**
   * Deserializes incoming JSON messages.
   * @param transaction The incoming transaction containing the message to deserialize.
   * @param next The next handler in the pipeline.
   */
  public async deserializer(transaction: IncomingTransaction, next: () => Promise<void>): Promise<void> {
    const message = transaction.incomingMessage;

    // Try to get the message type from headers
    const header = message.headers.get(Headers.MessageType);
    const type = header ? message.bus.messages.getTypeByHeader(header) : null;

    if (type === null && this.throwOnMissingType) {
      throw new Error('The type header is missing, invalid, or if the type cannot be found.');
    }

    // If we have a known type, we could potentially use it for validation
    // But since TypeScript doesn't have runtime type information like C#,
    // we'll just parse the JSON and trust the type system
    try {
      message.message = JSON.parse(message.body, this.jsonReviver);

      // If we found a type, we could set the messageType for consistency
      if (type !== null) {
        message.messageType = type;
      }
    } catch (error) {
      throw new Error(`Failed to parse JSON message body: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }

    await next();
  }

  /**
   * Serializes outgoing messages to JSON.
   * @param transaction The outgoing transaction containing messages to serialize.
   * @param next The next handler in the pipeline.
   */
  public async serializer(transaction: OutgoingTransaction, next: () => Promise<void>): Promise<void> {
    for (const message of transaction.outgoingMessages) {
      // Serialize the message to JSON
      try {
        message.body = JSON.stringify(message.message, this.jsonReplacer);
      } catch (error) {
        throw new Error(`Failed to serialize message to JSON: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }

      // Set content type
      message.headers.set(Headers.ContentType, this.contentType);

      // Try to get and set the message type header
      const header = message.bus.messages.getHeader(message.messageType);

      if (header !== null) {
        message.headers.set(Headers.MessageType, header);
      } else if (this.throwOnInvalidType) {
        throw new Error('The header has an invalid type.');
      }
    }

    await next();
  }
}
