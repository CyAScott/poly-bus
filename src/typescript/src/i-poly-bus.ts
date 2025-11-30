import { IncomingHandler } from './transport/transaction/message/handlers/incoming-handler';
import { IncomingMessage } from './transport/transaction/message/incoming-message';
import { ITransport } from './transport/i-transport';
import { Messages } from './transport/transaction/message/messages';
import { OutgoingHandler } from './transport/transaction/message/handlers/outgoing-handler';
import { Transaction } from './transport/transaction/transaction';
import { IncomingTransaction } from './transport/transaction/incoming-transaction';
import { OutgoingTransaction } from './transport/transaction/outgoing-transaction';

export interface IPolyBus {
  /**
   * The properties associated with this bus instance.
   */
  properties: Map<string, object>;

  /**
   * The transport mechanism used by this bus instance.
   */
  transport: ITransport;

  /**
   * Collection of handlers for processing incoming messages.
   */
  incomingPipeline: IncomingHandler[];

  /**
   * Collection of handlers for processing outgoing messages.
   */
  outgoingPipeline: OutgoingHandler[];

  /**
   * Collection of message types and their associated headers.
   */
  messages: Messages;

  /**
   * Creates a new incoming transaction.
   * @param incoming message to create the transaction from.
   * @returns A promise that resolves to the created incoming transaction.
   */
  createIncomingTransaction(message: IncomingMessage): Promise<IncomingTransaction>;

  /**
   * Creates a new outgoing transaction.
   * @returns A promise that resolves to the created outgoing transaction.
   */
  createOutgoingTransaction(): Promise<OutgoingTransaction>;

  /**
   * Sends messages associated with the given transaction to the transport.
   * @param transaction The transaction containing messages to send.
   * @returns A promise that resolves when the messages have been sent.
   */
  send(transaction: Transaction): Promise<void>;

  /**
   * Starts the bus and begins processing messages.
   * @returns A promise that resolves when the bus has started.
   */
  start(): Promise<void>;

  /**
   * Stops the bus and ceases processing messages.
   * @returns A promise that resolves when the bus has stopped.
   */
  stop(): Promise<void>;

  /**
   * The name of this bus instance.
   */
  name: string;
}
