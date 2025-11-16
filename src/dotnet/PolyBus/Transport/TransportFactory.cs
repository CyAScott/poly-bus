namespace PolyBus.Transport;

/// <summary>
/// Creates a transport instance to be used by PolyBus.
/// </summary>
public delegate Task<ITransport> TransportFactory(PolyBusBuilder builder, IPolyBus bus);
