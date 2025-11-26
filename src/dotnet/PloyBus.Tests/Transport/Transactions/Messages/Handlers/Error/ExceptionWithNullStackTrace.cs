namespace PolyBus.Transport.Transactions.Messages.Handlers.Error;

// Custom exception that returns null for StackTrace
class ExceptionWithNullStackTrace(string message) : Exception(message)
{
    public override string? StackTrace => null;
}
