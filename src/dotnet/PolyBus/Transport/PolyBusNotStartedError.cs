namespace PolyBus.Transport;

/// <summary>
/// A PolyBus error indicating that the bus has not been started.
/// </summary>
public class PolyBusNotStartedError()
    : PolyBusError(1, "PolyBus has not been started. Please call IPolyBus.Start() before using the bus.");
