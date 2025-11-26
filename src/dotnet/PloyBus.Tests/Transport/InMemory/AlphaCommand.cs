using PolyBus.Transport.Transactions.Messages;

namespace PolyBus.Transport.InMemory;

[MessageInfo(MessageType.Command, "alpha", "alpha-command", 1, 0, 0)]
class AlphaCommand
{
    public required string Name { get; set; }
}
