import { MessageInfo } from './transaction/message/message-info';
import { Transaction } from './transaction/transaction';

/**
 * An interface for a transport mechanism to send and receive messages.
 */
export interface ITransport {

  supportsCommandMessages: boolean;

  supportsDelayedMessages: boolean;

  supportsSubscriptions: boolean;

  /**
   * Sends messages associated with the given transaction to the transport.
   */
  // eslint-disable-next-line no-unused-vars
  send(transaction: Transaction): Promise<void>;

  /**
   * Subscribes to a messages so that the transport can start receiving them.
   */
  // eslint-disable-next-line no-unused-vars
  subscribe(messageInfo: MessageInfo): Promise<void>;

  /**
   * Enables the transport to start processing messages.
   */
  start(): Promise<void>;

  /**
   * Stops the transport from processing messages.
   */
  stop(): Promise<void>;
}
