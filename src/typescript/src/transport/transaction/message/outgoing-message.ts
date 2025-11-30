import { IPolyBus } from '../../../i-poly-bus';
import { Message } from './message';
import { MessageInfo } from './message-info';

/**
 * Represents an outgoing message in the transport layer.
 * Contains the message object, its type, and serialized body content.
 */
export class OutgoingMessage extends Message {
  private _body: string;
  private _endpoint: string | undefined;
  private _message: any;
  private _messageInfo: MessageInfo;
  private _messageType: Function;

  /**
   * Creates a new OutgoingMessage instance.
   * @param bus The bus instance associated with the message.
   * @param message The message object to be sent.
   * @param endpoint An optional location to explicitly send the message to.
   * @param messageInfo The message info describing metadata about the message.
   */
  constructor(bus: IPolyBus, message: any, endpoint?: string, messageInfo?: MessageInfo) {
    super(bus);
    this._message = message;
    this._messageType = message?.constructor || Object;
    this._body = '';
    this._endpoint = endpoint;
    this._messageInfo = messageInfo ?? bus.messages.getMessageInfo(message?.constructor) ?? new MessageInfo(
      0 as any,
      '',
      '',
      0,
      0,
      0
    );
  }

  /**
   * The message info describing metadata about the message.
   */
  public get messageInfo(): MessageInfo {
    return this._messageInfo;
  }

  public set messageInfo(value: MessageInfo) {
    this._messageInfo = value;
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
   * An optional location to explicitly send the message to.
   */
  public get endpoint(): string | undefined {
    return this._endpoint;
  }

  /**
   * Sets the endpoint for the message.
   */
  public set endpoint(value: string | undefined) {
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
