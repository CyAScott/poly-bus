/**
 * Base error class for PolyBus errors.
 */
export class PolyBusError extends Error {
  private readonly _errorCode: number;

  /**
   * Creates a new PolyBusError instance.
   * @param errorCode The error code associated with this error.
   * @param message The error message.
   */
  constructor(errorCode: number, message: string) {
    super(message);
    this._errorCode = errorCode;
    this.name = 'PolyBusError';

    // Maintains proper stack trace for where our error was thrown (only available on V8)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, PolyBusError);
    }
  }

  /**
   * Gets the error code associated with this error.
   */
  public get errorCode(): number {
    return this._errorCode;
  }
}
