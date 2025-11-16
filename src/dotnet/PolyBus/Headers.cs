using System.Diagnostics;

namespace PolyBus;

/// <summary>
/// Common header names used in PolyBus.
/// </summary>
[DebuggerStepThrough]
public static class Headers
{
    /// <summary>
    /// The content type header name used for specifying the message content type (e.g., "application/json").
    /// </summary>
    public const string ContentType = "content-type";

    /// <summary>
    /// The message type header name used for specifying the type of the message.
    /// </summary>
    public const string MessageType = "x-type";
}
