import { IPolyBus } from '../../i-poly-bus';
import { Transaction } from './transaction';

/**
 * Represents an outgoing transaction in the transport layer.
 * This is a simple transaction that extends the base Transaction class.
 */
export class OutgoingTransaction extends Transaction {
  /**
   * Creates a new OutgoingTransaction instance.
   * @param bus The bus instance associated with the transaction.
   */
  constructor(bus: IPolyBus) {
    super(bus);
  }
}
