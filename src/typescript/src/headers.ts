/**
 * Common header names used in PolyBus.
 */
export class Headers {
  /**
   * The correlation id header name used for specifying the correlation identifier for tracking related messages.
   */
  public static readonly CorrelationId = 'correlation-id';

  /**
   * The content type header name used for specifying the message content type (e.g., "application/json").
   */
  public static readonly ContentType = 'content-type';

  /**
   * The message type header name used for specifying the type of the message.
   */
  public static readonly MessageType = 'x-type';

  /**
   * The message id header name used for specifying the unique identifier of the message.
   */
  public static readonly RequestId = 'request-id';
}