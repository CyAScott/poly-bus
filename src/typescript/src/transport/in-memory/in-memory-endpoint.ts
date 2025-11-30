import { IPolyBus } from '../../i-poly-bus';
import { ITransport } from '../i-transport';
import { PolyBusNotStartedError } from '../poly-bus-not-started-error';
import { IncomingMessage } from '../transaction/message/incoming-message';
import { MessageInfo } from '../transaction/message/message-info';
import { Transaction } from '../transaction/transaction';

/**
 * An implementation of an in-memory transport endpoint.
 */
export class InMemoryEndpoint implements ITransport {
  constructor(
    private readonly broker: any,
    public readonly bus: IPolyBus
  ) {}

  /**
   * Handler for dead letter messages.
   */
  public deadLetterHandler?: (message: IncomingMessage) => void;

  /**
   * Whether the endpoint is active.
   */
  private _active: boolean = false;

  /**
   * The dead letter endpoint name.
   */
  public get deadLetterEndpoint(): string {
    return `${this.bus.name}.dead.letters`;
  }

  /**
   * If active, handles an incoming message by creating a transaction and executing the handlers for the bus.
   */
  public async handleMessage(message: IncomingMessage, isDeadLetter: boolean): Promise<void> {
    if (this._active) {
      if (isDeadLetter) {
        this.deadLetterHandler?.(message);
      } else {
        const transaction = await this.bus.createIncomingTransaction(message);
        await transaction.commit();
      }
    }
  }

  public handle(transaction: Transaction): Promise<void> {
    if (!this._active) {
      throw new PolyBusNotStartedError();
    }

    this.broker.send(transaction);

    return Promise.resolve();
  }

  public get supportsDelayedCommands(): boolean {
    return true;
  }

  public get supportsCommandMessages(): boolean {
    return true;
  }

  public async subscribe(messageInfo: MessageInfo): Promise<void> {
    if (!this._active) {
      throw new PolyBusNotStartedError();
    }

    this._subscriptions.add(messageInfo.toString(false));
  }

  public isSubscribed(messageInfo: MessageInfo): boolean {
    return this._subscriptions.has(messageInfo.toString(false));
  }

  public get supportsSubscriptions(): boolean {
    return true;
  }

  private readonly _subscriptions = new Set<string>();

  public async start(): Promise<void> {
    this._active = true;
  }

  public async stop(): Promise<void> {
    this._active = false;
  }
}
