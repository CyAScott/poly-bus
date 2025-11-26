using System.Diagnostics;

namespace PolyBus;

/// <summary>
/// Common header names used in PolyBus.
/// </summary>
[DebuggerStepThrough]
public static class Headers
{
    /// <summary>
    /// The correlation id header name used for specifying the correlation identifier for tracking related messages.
    /// </summary>
    public const string CorrelationId = "correlation-id";

    /// <summary>
    /// The content type header name used for specifying the message content type (e.g., "application/json").
    /// </summary>
    public const string ContentType = "content-type";

    /// <summary>
    /// The message type header name used for specifying the type of the message.
    /// </summary>
    public const string MessageType = "x-type";

    /// <summary>
    /// The message id header name used for specifying the unique identifier of the message.
    /// </summary>
    public const string RequestId = "request-id";
}
