import { IncomingMessage } from './message/incoming-message';
import { IPolyBus } from '../../i-poly-bus';
import { PolyBusBuilder } from '../../poly-bus-builder';
import { IncomingTransaction } from './incoming-transaction';

/**
 * A method for creating a new transaction for processing a request.
 * This should be used to integrate with external transaction systems to ensure message processing
 * is done within the context of a transaction.
 */
export type IncomingTransactionFactory = (builder: PolyBusBuilder, bus: IPolyBus, message: IncomingMessage) => Promise<IncomingTransaction>;
