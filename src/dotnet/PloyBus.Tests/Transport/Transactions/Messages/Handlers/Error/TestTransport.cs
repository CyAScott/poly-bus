namespace PolyBus.Transport.Transactions.Messages.Handlers.Error;

class TestTransport : ITransport
{
    public const string DefaultDeadLetterEndpoint = "dead-letters";
    public string DeadLetterEndpoint => DefaultDeadLetterEndpoint;
    public Task Handle(Transaction transaction) => throw new NotImplementedException();
    public bool SupportsCommandMessages => true;
    public bool SupportsDelayedCommands => true;
    public bool SupportsSubscriptions => false;

    public Task Send(Transaction transaction) => Task.CompletedTask;
    public Task Subscribe(MessageInfo messageInfo) => Task.CompletedTask;
    public Task Start() => Task.CompletedTask;
    public Task Stop() => Task.CompletedTask;
}
