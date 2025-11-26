using System.Diagnostics;
using PolyBus.Transport.Transactions;

namespace PolyBus.Transport.InMemory;

[DebuggerStepThrough]
class TestEndpoint
{
    public Func<IncomingTransaction, Task> OnMessageReceived { get; set; } = _ => Task.CompletedTask;
    public IPolyBus Bus { get; set; } = null!;
    public PolyBusBuilder Builder { get; } = new();
    public InMemoryEndpoint Transport => (InMemoryEndpoint)Bus.Transport;
    public async Task Handler(IncomingTransaction transaction, Func<Task> next)
    {
        await OnMessageReceived(transaction);
        await next();
    }
}
