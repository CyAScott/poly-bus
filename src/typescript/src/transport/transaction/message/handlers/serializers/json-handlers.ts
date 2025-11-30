import { Headers } from '../../../../../headers';
import { IncomingTransaction } from '../../../incoming-transaction';
import { OutgoingTransaction } from '../../../outgoing-transaction';

/**
 * Handlers for serializing and deserializing messages as JSON.
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
   * The header key to use for the content type.
   */
  public header: string = Headers.ContentType;

  /**
   * Deserializes incoming messages from JSON.
   */
  public async deserializer(transaction: IncomingTransaction, next: () => Promise<void>): Promise<void> {
    const incomingMessage = transaction.incomingMessage;

    incomingMessage.message = JSON.parse(incomingMessage.body, this.jsonReviver);

    await next();
  }

  /**
   * Serializes outgoing messages to JSON.
   */
  public async serializer(transaction: OutgoingTransaction, next: () => Promise<void>): Promise<void> {
    for (const message of transaction.outgoingMessages) {
      message.body = JSON.stringify(message.message, this.jsonReplacer);
      message.headers.set(this.header, this.contentType);
    }
    await next();
  }
}
