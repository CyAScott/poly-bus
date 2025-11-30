import { PolyBusError } from '../../../poly-bus-error';

/**
 * Is thrown when a requested type, attribute/decorator, or header was not registered with the message system.
 */
export class PolyBusMessageNotFoundError extends PolyBusError {
  /**
   * Creates a new PolyBusMessageNotFoundError instance.
   */
  constructor() {
    super(2, 'The requested type, attribute/decorator, or header was not found.');
    this.name = 'PolyBusMessageNotFoundError';

    // Maintains proper stack trace for where our error was thrown (only available on V8)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, PolyBusMessageNotFoundError);
    }
  }
}
