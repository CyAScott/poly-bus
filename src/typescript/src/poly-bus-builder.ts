
import { IPolyBus } from './i-poly-bus';
import { ITransport } from './transport/i-transport';
import { IncomingHandler } from './transport/transaction/message/handlers/incoming-handler';
import { OutgoingHandler } from './transport/transaction/message/handlers/outgoing-handler';
import { Messages } from './transport/transaction/message/messages';
import { IncomingTransactionFactory } from './transport/transaction/incoming-transaction-factory';
import { OutgoingTransactionFactory } from './transport/transaction/outgoing-transaction-factory';
import { IncomingTransaction } from './transport/transaction/incoming-transaction';
import { OutgoingTransaction } from './transport/transaction/outgoing-transaction';
import { PolyBus } from './poly-bus';
import { InMemoryMessageBroker } from './transport/in-memory/in-memory-message-broker';

/**
 * A factory method for creating the transport for the PolyBus instance.
 * The transport is responsible for sending and receiving messages.
 */
export type TransportFactory = (builder: PolyBusBuilder, bus: IPolyBus) => Promise<ITransport>;

/**
 * Builder class for configuring and creating PolyBus instances.
 */
export class PolyBusBuilder {
  /**
   * The incoming transaction factory will be used to create incoming transactions for handling messages.
   */
  public incomingTransactionFactory: IncomingTransactionFactory = (_, bus, message) => {
    return Promise.resolve(new IncomingTransaction(bus, message));
  };

  /**
   * The outgoing transaction factory will be used to create outgoing transactions for sending messages.
   */
  public outgoingTransactionFactory: OutgoingTransactionFactory = (_, bus) => {
    return Promise.resolve(new OutgoingTransaction(bus));
  };

  /**
   * The transport factory will be used to create the transport for the PolyBus instance.
   * The transport is responsible for sending and receiving messages.
   */
  public transportFactory: TransportFactory = async (builder, bus) => {
    const transport = new InMemoryMessageBroker();
    return transport.addEndpoint(builder, bus);
  };

  /**
   * The properties associated with this bus instance.
   */
  public properties: Map<string, object> = new Map<string, object>();

  /**
   * Collection of handlers for processing incoming messages.
   */
  public incomingPipeline: IncomingHandler[] = [];

  /**
   * Collection of handlers for processing outgoing messages.
   */
  public outgoingPipeline: OutgoingHandler[] = [];

  /**
   * Collection of message types and their associated headers.
   */
  public messages: Messages = new Messages();

  /**
   * The name of this bus instance.
   */
  public name: string = 'polybus';

  /**
   * Builds and configures a new PolyBus instance.
   * @returns A promise that resolves to the configured PolyBus instance.
   */
  public async build(): Promise<IPolyBus> {
    const bus = new PolyBus(this);
    bus.transport = await this.transportFactory(this, bus);
    return bus;
  }
}
