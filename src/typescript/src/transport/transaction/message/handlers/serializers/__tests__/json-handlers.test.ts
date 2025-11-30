import { describe, it, expect, beforeEach } from '@jest/globals';
import { JsonHandlers } from '../json-handlers';
import { Messages } from '../../../messages';
import { messageInfo } from '../../../message-info';
import { MessageType } from '../../../message-type';
import { Headers } from '../../../../../../headers';
import { OutgoingTransaction } from '../../../../outgoing-transaction';
import { IPolyBus } from '../../../../../../i-poly-bus';
import { ITransport } from '../../../../../i-transport';
import { IncomingTransaction } from '../../../../incoming-transaction';
import { IncomingMessage } from '../../../incoming-message';

@messageInfo(MessageType.Command, 'polybus', 'json-handler-test-message', 1, 0, 0)
class JsonHandlerTestMessage {
  public text: string = '';
}

describe('JsonHandlers', () => {
  let jsonHandlers: JsonHandlers;
  let messages: Messages;

  beforeEach(() => {
    jsonHandlers = new JsonHandlers();
    messages = new Messages();
    messages.add(JsonHandlerTestMessage);
  });

  it('Serializer_SetsBodyAndContentType', async () => {
    // Arrange
    const message = new JsonHandlerTestMessage();
    message.text = 'Hello, World!';

    const mockBus: IPolyBus = {
      transport: {} as ITransport,
      incomingPipeline: [],
      outgoingPipeline: [],
      messages: messages,
      name: 'MockBus',
      properties: new Map<string, object>(),
      createIncomingTransaction: async (msg: IncomingMessage) => new IncomingTransaction(mockBus, msg),
      createOutgoingTransaction: async () => new OutgoingTransaction(mockBus),
      send: async () => {},
      start: async () => {},
      stop: async () => {}
    } as any;

    const transaction = new OutgoingTransaction(mockBus);
    const outgoingMessage = transaction.add(message);

    // Act
    await jsonHandlers.serializer(transaction, async () => {});

    // Assert
    expect(outgoingMessage.body).not.toBeNull();
    expect(outgoingMessage.headers.get(Headers.ContentType)).toBe('application/json');
  });
});
