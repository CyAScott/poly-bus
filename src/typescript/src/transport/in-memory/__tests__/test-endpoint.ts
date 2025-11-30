import { IPolyBus } from '../../../i-poly-bus';
import { PolyBusBuilder } from '../../../poly-bus-builder';
import { IncomingTransaction } from '../../transaction/incoming-transaction';
import { InMemoryEndpoint } from '../in-memory-endpoint';

/**
 * Represents a test endpoint with bus and handlers
 */
export class TestEndpoint {
  public onMessageReceived: (transaction: IncomingTransaction) => Promise<void> = async () => {};
  public bus!: IPolyBus;
  public readonly builder: PolyBusBuilder = new PolyBusBuilder();

  public get transport(): InMemoryEndpoint {
    return this.bus.transport as InMemoryEndpoint;
  }

  public async handler(transaction: IncomingTransaction, next: () => Promise<void>): Promise<void> {
    await this.onMessageReceived(transaction);
    await next();
  }
}
