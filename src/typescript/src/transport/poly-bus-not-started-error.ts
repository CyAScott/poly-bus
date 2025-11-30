import { PolyBusError } from '../poly-bus-error';

/**
 * A PolyBus error indicating that the bus has not been started.
 */
export class PolyBusNotStartedError extends PolyBusError {
  /**
   * Creates a new PolyBusNotStartedError instance.
   */
  constructor() {
    super(1, 'PolyBus has not been started. Please call IPolyBus.start() before using the bus.');
    this.name = 'PolyBusNotStartedError';

    // Maintains proper stack trace for where our error was thrown (only available on V8)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, PolyBusNotStartedError);
    }
  }
}
