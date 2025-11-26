using PolyBus.Transport.Transactions.Messages;

namespace PolyBus.Transport.InMemory;

[MessageInfo(MessageType.Event, "alpha", "alpha-event", 1, 0, 0)]
class AlphaEvent
{
    public required string Name { get; set; }
}
