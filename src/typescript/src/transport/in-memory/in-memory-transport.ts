import { IncomingMessage } from '../transaction/message/incoming-message';
import { IncomingTransaction } from '../transaction/incoming-transaction';
import { IPolyBus } from '../../i-poly-bus';
import { ITransport } from '../i-transport';
import { MessageInfo } from '../transaction/message/message-info';
import { OutgoingMessage } from '../transaction/message/outgoing-message';
import { PolyBusBuilder } from '../../poly-bus-builder';
import { Transaction } from '../transaction/transaction';

export class InMemoryTransport {
  public addEndpoint(_builder: PolyBusBuilder, bus: IPolyBus): ITransport {
    const endpoint = new Endpoint(this, bus);
    this._endpoints.set(bus.name, endpoint);
    return endpoint;
  }
  private readonly _endpoints = new Map<string, Endpoint>();

  public async send(transaction: Transaction): Promise<void> {
    if (!this._active) {
      throw new Error('Transport is not active.');
    }

    if (transaction.outgoingMessages.length === 0) {
      return;
    }

    let promiseResolver: () => void = () => {};
    const transactionId = Math.random().toString(36).substring(2, 11);
    const promise = new Promise<void>((resolve) => {
      promiseResolver = resolve;
    });
    this._transactions.set(transactionId, promise);

    try {
      const tasks: Promise<void>[] = [];

      for (const message of transaction.outgoingMessages) {
        if (message.deliverAt) {
          let delay = message.deliverAt.getTime() - Date.now();
          if (delay > 0) {
            // eslint-disable-next-line no-undef
            const timeoutId = setTimeout(async () => {
              try {
                const transaction = await message.bus.createTransaction();
                message.deliverAt = undefined;
                transaction.outgoingMessages.push(message);
                await transaction.commit();
              } catch (error) {
                // eslint-disable-next-line no-undef
                console.error('Error delivering delayed message:', error);
              } finally {
                this._timeouts.delete(transactionId);
              }
            }, delay);
            this._timeouts.set(transactionId, timeoutId);
            continue;
          }
        }
        for (const endpoint of this._endpoints.values()) {
          const task = endpoint.handle(message);
          tasks.push(task);
        }
      }

      await Promise.all(tasks);
    } finally {
      promiseResolver();
      this._transactions.delete(transactionId);
    }
  }
  // eslint-disable-next-line no-undef
  private readonly _timeouts = new Map<string, NodeJS.Timeout>();

  public useSubscriptions: boolean = false;

  public async start(): Promise<void> {
    this._active = true;
  }
  private _active: boolean = false;

  public async stop(): Promise<void> {
    this._active = false;
    for (const timeoutId of this._timeouts.values()) {
      // eslint-disable-next-line no-undef
      clearTimeout(timeoutId);
    }
    this._timeouts.clear();
    await Promise.all(this._transactions.values());
    this._transactions.clear();
  }
  private readonly _transactions = new Map<string, Promise<void>>();
}

class Endpoint implements ITransport {
  constructor(
    private readonly transport: InMemoryTransport,
    private readonly bus: IPolyBus
  ) {}

  public async handle(message: OutgoingMessage): Promise<void> {
    if (!this.transport.useSubscriptions || this._subscriptions.includes(message.messageType)) {
      const incomingMessage = new IncomingMessage(this.bus, message.body);
      incomingMessage.headers = message.headers;

      try {
        const transaction = await this.bus.createTransaction(incomingMessage) as IncomingTransaction;
        await transaction.commit();
      } catch (error) {
        console.error('Error processing message:', error);
      }
    }
  }

  private readonly _subscriptions: Function[] = [];
  public async subscribe(messageInfo: MessageInfo): Promise<void> {
    const type = this.bus.messages.getTypeByMessageInfo(messageInfo);
    if (!type) {
      throw new Error(`Message type for attribute ${messageInfo.toString()} is not registered.`);
    }
    this._subscriptions.push(type);
  }

  public get supportsCommandMessages(): boolean {
    return true;
  }

  public get supportsDelayedMessages(): boolean {
    return true;
  }

  public get supportsSubscriptions(): boolean {
    return true;
  }

  public async send(transaction: Transaction): Promise<void> {
    return this.transport.send(transaction);
  }

  public async start(): Promise<void> {
    return this.transport.start();
  }

  public async stop(): Promise<void> {
    return this.transport.stop();
  }
}
