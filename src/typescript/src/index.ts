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
export { IncomingTransactionFactory } from './transport/transaction/incoming-transaction-factory';
export { InMemoryEndpoint } from './transport/in-memory/in-memory-endpoint';
export { InMemoryMessageBroker } from './transport/in-memory/in-memory-message-broker';
export { IPolyBus } from './i-poly-bus';
export { ITransport } from './transport/i-transport';
export { JsonHandlers } from './transport/transaction/message/handlers/serializers/json-handlers';
export { Message } from './transport/transaction/message/message';
export { MessageInfo, MessageInfoMetadata, messageInfo, MessageType } from './transport/transaction/message/message-info';
export { Messages } from './transport/transaction/message/messages';
export { OutgoingHandler } from './transport/transaction/message/handlers/outgoing-handler';
export { OutgoingMessage } from './transport/transaction/message/outgoing-message';
export { OutgoingTransaction } from './transport/transaction/outgoing-transaction';
export { OutgoingTransactionFactory } from './transport/transaction/outgoing-transaction-factory';
export { PolyBus } from './poly-bus';
export { PolyBusBuilder, TransportFactory } from './poly-bus-builder';
export { PolyBusError } from './poly-bus-error';
export { PolyBusMessageNotFoundError } from './transport/transaction/message/poly-bus-message-not-found-error';
export { PolyBusNotStartedError } from './transport/poly-bus-not-started-error';
export { Transaction } from './transport/transaction/transaction';
