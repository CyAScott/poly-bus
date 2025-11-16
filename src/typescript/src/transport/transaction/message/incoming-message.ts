import { IPolyBus } from '../../../i-poly-bus';
import { Message } from './message';

/**
 * Represents an incoming message in the transport layer.
 * Contains the message body, deserialized message object, and message type information.
 */
export class IncomingMessage extends Message {
  private _messageType: any;
  private _body: string;
  private _message: any;

  /**
   * Creates a new IncomingMessage instance.
   * @param bus The bus instance associated with the message.
   * @param body The message body contents.
   * @param message The deserialized message object (optional, defaults to body).
   * @param messageType The type of the message (optional, defaults to string).
   */
  constructor(bus: IPolyBus, body: string, message?: any, messageType?: any) {
    super(bus);

    if (!body) {
      throw new Error('Body parameter cannot be null or undefined');
    }

    this._body = body;
    this._message = message ?? body;
    this._messageType = messageType ?? String;
  }

  /**
   * The default is string, but can be changed based on deserialization.
   */
  public get messageType(): any {
    return this._messageType;
  }

  public set messageType(value: any) {
    this._messageType = value;
  }

  /**
   * The message body contents.
   */
  public get body(): string {
    return this._body;
  }

  public set body(value: string) {
    this._body = value;
  }

  /**
   * The deserialized message object, otherwise the same value as Body.
   */
  public get message(): any {
    return this._message;
  }

  public set message(value: any) {
    this._message = value;
  }
}
