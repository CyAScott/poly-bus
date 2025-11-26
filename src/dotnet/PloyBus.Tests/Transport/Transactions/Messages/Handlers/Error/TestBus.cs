namespace PolyBus.Transport.Transactions.Messages.Handlers.Error;

class TestBus(string name) : IPolyBus
{
    public IDictionary<string, object> Properties { get; } = new Dictionary<string, object>();
    public ITransport Transport { get; } = new TestTransport();
    public IList<IncomingHandler> IncomingPipeline { get; } = [];
    public IList<OutgoingHandler> OutgoingPipeline { get; } = [];
    public Messages Messages { get; } = new();
    public Task<IncomingTransaction> CreateIncomingTransaction(IncomingMessage message) =>
        Task.FromResult(new IncomingTransaction(this, message));
    public Task<OutgoingTransaction> CreateOutgoingTransaction() =>
        Task.FromResult(new OutgoingTransaction(this));
    public string Name { get; } = name;
    public Task Send(Transaction transaction) => Task.CompletedTask;
    public Task Start() => Task.CompletedTask;
    public Task Stop() => Task.CompletedTask;
}
