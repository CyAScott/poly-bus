import { IPolyBus } from '../../i-poly-bus';
import { OutgoingMessage } from './message/outgoing-message';

/**
 * Represents a transaction in the transport layer.
 * Contains the bus instance, state dictionary, and outgoing messages to be sent when committed.
 */
export class Transaction {
  private readonly _bus: IPolyBus;
  private readonly _state: Map<string, any> = new Map<string, any>();
  private readonly _outgoingMessages: OutgoingMessage[] = [];

  /**
   * Creates a new Transaction instance.
   * @param bus The bus instance associated with the transaction.
   */
  constructor(bus: IPolyBus) {
    if (!bus) {
      throw new Error('Bus parameter cannot be null or undefined');
    }
    this._bus = bus;
  }

  /**
   * The bus instance associated with the transaction.
   */
  public get bus(): IPolyBus {
    return this._bus;
  }

  /**
   * State dictionary that can be used to store arbitrary data associated with the transaction.
   */
  public get state(): Map<string, any> {
    return this._state;
  }

  /**
   * A list of outgoing messages to be sent when the transaction is committed.
   */
  public get outgoingMessages(): OutgoingMessage[] {
    return this._outgoingMessages;
  }

  /**
   * Adds an outgoing message to be sent when the transaction is committed.
   * @param message The message object to be sent.
   * @returns The OutgoingMessage instance that was added.
   */
  public addOutgoingMessage(message: any, endpoint: string | null = null): OutgoingMessage {
    function getEndpoint(bus: IPolyBus): string {
      const messageInfo = bus.messages.getMessageInfo(message.constructor);
      if (!messageInfo) {
        throw new Error(`Message type ${message.constructor.name} is not registered on bus ${bus.name}.`);
      }
      return messageInfo.endpoint;
    }
    const outgoingMessage = new OutgoingMessage(this._bus, message, endpoint ?? getEndpoint(this.bus));
    this._outgoingMessages.push(outgoingMessage);
    return outgoingMessage;
  }

  /**
   * If an exception occurs during processing, the transaction will be aborted.
   */
  public async abort(): Promise<void> {
    // Default implementation - can be overridden in subclasses
  }

  /**
   * If no exception occurs during processing, the transaction will be committed.
   */
  public async commit(): Promise<void> {
    return this._bus.send(this);
  }
}
