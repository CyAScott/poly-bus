import { IPolyBus } from '../i-poly-bus';
import { ITransport } from '../transport/i-transport';
import { PolyBusBuilder } from '../poly-bus-builder';

/**
 * Creates a transport instance to be used by PolyBus.
 */
// eslint-disable-next-line no-unused-vars
export type TransportFactory = (builder: PolyBusBuilder, bus: IPolyBus) => Promise<ITransport>;
