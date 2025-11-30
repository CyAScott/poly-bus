import { MessageInfo } from './transaction/message/message-info';
import { Transaction } from './transaction/transaction';

/**
 * An interface for a transport mechanism to send and receive messages.
 */
export interface ITransport {

  /**
   * Where messages that cannot be delivered are sent.
   */
  deadLetterEndpoint: string;

  /**
   * If the transport supports sending command messages, this will be true.
   */
  supportsCommandMessages: boolean;

  /**
   * If the transport supports sending delayed commands, this will be true.
   */
  supportsDelayedCommands: boolean;

  /**
   * If the transport supports event message subscriptions, this will be true.
   */
  supportsSubscriptions: boolean;

  /**
   * Sends messages associated with the given transaction to the transport.
   */
  // eslint-disable-next-line no-unused-vars
  handle(transaction: Transaction): Promise<void>;

  /**
   * Subscribes to a messages so that the transport can start receiving them.
   */
  // eslint-disable-next-line no-unused-vars
  subscribe(messageInfo: MessageInfo): Promise<void>;

  /**
   * Starts the transport to start processing messages.
   */
  start(): Promise<void>;

  /**
   * Stops the transport from processing messages.
   */
  stop(): Promise<void>;
}
