import { IPolyBus } from '../../../i-poly-bus';
import { Message } from './message';

/**
 * Represents an outgoing message in the transport layer.
 * Contains the message object, its type, and serialized body content.
 */
export class OutgoingMessage extends Message {
  private _body: string;
  private _endpoint: string;
  private _message: any;
  private _messageType: Function;

  /**
   * Creates a new OutgoingMessage instance.
   * @param bus The bus instance associated with the message.
   * @param message The message object to be sent.
   */
  constructor(bus: IPolyBus, message: any, endpoint: string) {
    super(bus);
    this._message = message;
    this._messageType = message?.constructor || Object;
    this._body = message?.toString() || '';
    this._endpoint = endpoint;
  }

  /**
   * If the transport supports delayed messages, this is the time at which the message should be delivered.
   */
  public deliverAt: Date | undefined;

  /**
   * Gets the type of the message.
   */
  public get messageType(): Function {
    return this._messageType;
  }

  /**
   * Sets the type of the message.
   */
  public set messageType(value: Function) {
    this._messageType = value;
  }

  /**
   * The serialized message body contents.
   */
  public get body(): string {
    return this._body;
  }

  /**
   * Sets the serialized message body contents.
   */
  public set body(value: string) {
    this._body = value;
  }

  /**
   * If the message is a command then this is the endpoint the message is being sent to.
   * If the message is an event then this is the source endpoint the message is being sent from.
   */
  public get endpoint(): string {
    return this._endpoint;
  }

  /**
   * Sets the endpoint for the message.
   */
  public set endpoint(value: string) {
    this._endpoint = value;
  }

  /**
   * The message object.
   */
  public get message(): any {
    return this._message;
  }

  /**
   * Sets the message object.
   */
  public set message(value: any) {
    this._message = value;
  }
}
