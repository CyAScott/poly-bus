import { OutgoingTransaction } from '../../outgoing-transaction';

/**
 * A method for handling outgoing messages to the transport.
 */
export type OutgoingHandler = (transaction: OutgoingTransaction, next: () => Promise<void>) => Promise<void>;
