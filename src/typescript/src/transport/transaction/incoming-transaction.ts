import { IncomingMessage } from './message/incoming-message';
import { IPolyBus } from '../../i-poly-bus';
import { Transaction } from './transaction';

/**
 * Represents an incoming transaction in the transport layer.
 * Contains the incoming message from the transport being processed.
 */
export class IncomingTransaction extends Transaction {
  private readonly _incomingMessage: IncomingMessage;

  /**
   * Creates a new IncomingTransaction instance.
   * @param bus The bus instance associated with the transaction.
   * @param incomingMessage The incoming message from the transport being processed.
   */
  constructor(bus: IPolyBus, incomingMessage: IncomingMessage) {
    super(bus);

    if (!incomingMessage) {
      throw new Error('IncomingMessage parameter cannot be null or undefined');
    }

    this._incomingMessage = incomingMessage;
  }

  /**
   * The incoming message from the transport being processed.
   */
  public get incomingMessage(): IncomingMessage {
    return this._incomingMessage;
  }
}
