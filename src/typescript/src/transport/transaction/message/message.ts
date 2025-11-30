import { IPolyBus } from '../../../i-poly-bus';

/**
 * Message class that represents a message in the transport layer.
 * Contains state dictionary, headers, and reference to the bus instance.
 */
export class Message {
  private readonly _bus: IPolyBus;

  /**
   * Creates a new Message instance.
   * @param bus The bus instance associated with the message.
   */
  constructor(bus: IPolyBus) {
    if (!bus) {
      throw new Error('Bus parameter cannot be null or undefined');
    }
    this._bus = bus;
  }

  /**
   * State dictionary that can be used to store arbitrary data associated with the message.
   */
  public state: Map<string, any> = new Map<string, any>();

  /**
   * Message headers from the transport.
   */
  public headers: Map<string, string> = new Map<string, string>();

  /**
   * The bus instance associated with the message.
   */
  public get bus(): IPolyBus {
    return this._bus;
  }
}
