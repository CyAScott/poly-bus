namespace PolyBus.Transport.Transactions.Messages;

/// <summary>
/// Is thrown when a requested type, attribute/decorator, or header was registered with the message system.
/// </summary>
public class PolyBusMessageNotFoundError()
    : PolyBusError(2, "The requested type, attribute/decorator, or header was not found.");
