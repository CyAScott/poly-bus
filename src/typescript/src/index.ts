/**
 * poly-bus - A TypeScript NPM package for both browser and Node.js environments
 */

// Import reflect-metadata for decorator support
import 'reflect-metadata';

// Export message-related types and decorators
export { ErrorHandler } from './transport/transaction/message/handlers/error/error-handlers';
export { Headers } from './headers';
export { IncomingHandler } from './transport/transaction/message/handlers/incoming-handler';
export { IncomingMessage } from './transport/transaction/message/incoming-message';
export { IncomingTransaction } from './transport/transaction/incoming-transaction';
export { InMemoryTransport } from './transport/in-memory/in-memory-transport';
export { ITransport } from './transport/i-transport';
export { IPolyBus } from './i-poly-bus';
export { JsonHandlers } from './transport/transaction/message/handlers/serializers/json-handlers';
export { Message } from './transport/transaction/message/message';
export { MessageInfo, messageInfo, MessageType } from './transport/transaction/message/message-info';
export { Messages } from './transport/transaction/message/messages';
export { OutgoingHandler } from './transport/transaction/message/handlers/outgoing-handler';
export { OutgoingMessage } from './transport/transaction/message/outgoing-message';
export { OutgoingTransaction } from './transport/transaction/outgoing-transaction';
export { PolyBus } from './poly-bus';
export { PolyBusBuilder } from './poly-bus-builder';
export { Transaction } from './transport/transaction/transaction';
export { TransactionFactory } from './transport/transaction/transaction-factory';
export { TransportFactory } from './poly-bus-builder';
