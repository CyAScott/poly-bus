import { IPolyBus } from './i-poly-bus';
import { ITransport } from './transport/i-transport';
import { IncomingHandler } from './transport/transaction/message/handlers/incoming-handler';
import { OutgoingHandler } from './transport/transaction/message/handlers/outgoing-handler';
import { Messages } from './transport/transaction/message/messages';
import { Transaction } from './transport/transaction/transaction';
import { IncomingTransaction } from './transport/transaction/incoming-transaction';
import { OutgoingTransaction } from './transport/transaction/outgoing-transaction';
import { IncomingMessage } from './transport/transaction/message/incoming-message';
import { PolyBusBuilder } from './poly-bus-builder';

/**
 * Implementation of IPolyBus that provides message handling and transport functionality.
 */
export class PolyBus implements IPolyBus {
  private _transport!: ITransport;
  private readonly _incomingHandlers: IncomingHandler[];
  private readonly _outgoingHandlers: OutgoingHandler[];
  private readonly _messages: Messages;
  private readonly _name: string;
  private readonly _builder: PolyBusBuilder;

  /**
   * Creates a new PolyBus instance.
   * @param builder The builder containing configuration for this bus instance.
   */
  constructor(builder: PolyBusBuilder) {
    this._builder = builder;
    this._incomingHandlers = builder.incomingHandlers;
    this._outgoingHandlers = builder.outgoingHandlers;
    this._messages = builder.messages;
    this._name = builder.name;
  }

  /**
   * The properties associated with this bus instance.
   */
  public get properties(): Map<string, object> {
    return this._builder.properties;
  }

  /**
   * The transport mechanism used by this bus instance.
   */
  public get transport(): ITransport {
    return this._transport;
  }

  public set transport(value: ITransport) {
    this._transport = value;
  }

  /**
   * Collection of handlers for processing incoming messages.
   */
  public get incomingHandlers(): IncomingHandler[] {
    return this._incomingHandlers;
  }

  /**
   * Collection of handlers for processing outgoing messages.
   */
  public get outgoingHandlers(): OutgoingHandler[] {
    return this._outgoingHandlers;
  }

  /**
   * Collection of message types and their associated headers.
   */
  public get messages(): Messages {
    return this._messages;
  }

  /**
   * The name of this bus instance.
   */
  public get name(): string {
    return this._name;
  }

  /**
   * Creates a new transaction, optionally based on an incoming message.
   * @param message Optional incoming message to create the transaction from.
   * @returns A promise that resolves to the created transaction.
   */
  public async createTransaction(message?: IncomingMessage): Promise<Transaction> {
    return this._builder.transactionFactory(this._builder, this, message);
  }

  /**
   * Sends messages associated with the given transaction to the transport.
   * Applies appropriate handlers based on transaction type before sending.
   * @param transaction The transaction containing messages to send.
   * @returns A promise that resolves when the messages have been sent.
   */
  public async send(transaction: Transaction): Promise<void> {
    let step = () => this.transport.send(transaction);

    if (transaction instanceof IncomingTransaction) {
      const handlers = transaction.bus.incomingHandlers;
      for (let index = handlers.length - 1; index >= 0; index--) {
        const handler = handlers[index];
        const next = step;
        step = () => handler(transaction, next);
      }
    } else if (transaction instanceof OutgoingTransaction) {
      const handlers = transaction.bus.outgoingHandlers;
      for (let index = handlers.length - 1; index >= 0; index--) {
        const handler = handlers[index];
        const next = step;
        step = () => handler(transaction, next);
      }
    }

    try {
      await step();
    } catch (error) {
      await transaction.abort();
      throw error;
    }
  }

  /**
   * Starts the bus and begins processing messages.
   * @returns A promise that resolves when the bus has started.
   */
  public async start(): Promise<void> {
    return this.transport.start();
  }

  /**
   * Stops the bus and ceases processing messages.
   * @returns A promise that resolves when the bus has stopped.
   */
  public async stop(): Promise<void> {
    return this.transport.stop();
  }
}
