import { IncomingTransaction } from '../../incoming-transaction';

/**
 * A method for handling incoming messages from the transport.
 */
export type IncomingHandler = (transaction: IncomingTransaction, next: () => Promise<void>) => Promise<void>;
