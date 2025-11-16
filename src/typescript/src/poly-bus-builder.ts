
import { IPolyBus } from './i-poly-bus';
import { ITransport } from './transport/i-transport';
import { IncomingHandler } from './transport/transaction/message/handlers/incoming-handler';
import { OutgoingHandler } from './transport/transaction/message/handlers/outgoing-handler';
import { Messages } from './transport/transaction/message/messages';
import { TransactionFactory } from './transport/transaction/transaction-factory';
import { IncomingTransaction } from './transport/transaction/incoming-transaction';
import { OutgoingTransaction } from './transport/transaction/outgoing-transaction';
import { PolyBus } from './poly-bus';

/**
 * A factory method for creating the transport for the PolyBus instance.
 * The transport is responsible for sending and receiving messages.
 */
export type TransportFactory = (builder: PolyBusBuilder, bus: IPolyBus) => Promise<ITransport>;

/**
 * Builder class for configuring and creating PolyBus instances.
 */
export class PolyBusBuilder {
  private _transactionFactory: TransactionFactory;
  private _transportFactory: TransportFactory;
  private readonly _incomingHandlers: IncomingHandler[] = [];
  private readonly _outgoingHandlers: OutgoingHandler[] = [];
  private readonly _messages: Messages = new Messages();
  private _name: string = 'PolyBusInstance';

  /**
   * Creates a new PolyBusBuilder instance.
   */
  constructor() {
    // Default transaction factory - creates IncomingTransaction for incoming messages,
    // OutgoingTransaction for outgoing messages
    this._transactionFactory = (_, bus, message) => {
      return Promise.resolve(
        message != null
          ? new IncomingTransaction(bus, message)
          : new OutgoingTransaction(bus)
      );
    };

    // Default transport factory - should be overridden by specific transport implementations
    this._transportFactory = async (_builder, _bus) => {
      throw new Error('Transport factory must be configured before building PolyBus. Use a transport-specific builder method.');
    };
  }

  /**
   * The transaction factory will be used to create transactions for message handling.
   * Transactions are used to ensure that a group of messages related to a single request
   * are sent to the transport in a single atomic operation.
   */
  public get transactionFactory(): TransactionFactory {
    return this._transactionFactory;
  }

  public set transactionFactory(value: TransactionFactory) {
    this._transactionFactory = value;
  }

  /**
   * The transport factory will be used to create the transport for the PolyBus instance.
   * The transport is responsible for sending and receiving messages.
   */
  public get transportFactory(): TransportFactory {
    return this._transportFactory;
  }

  public set transportFactory(value: TransportFactory) {
    this._transportFactory = value;
  }

  /**
   * The properties associated with this bus instance.
   */
  properties: Map<string, object> = new Map<string, object>();

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

  public set name(value: string) {
    this._name = value;
  }

  /**
   * Builds and configures a new PolyBus instance.
   * @returns A promise that resolves to the configured PolyBus instance.
   */
  public async build(): Promise<IPolyBus> {
    const bus = new PolyBus(this);
    bus.transport = await this._transportFactory(this, bus);
    return bus;
  }
}
