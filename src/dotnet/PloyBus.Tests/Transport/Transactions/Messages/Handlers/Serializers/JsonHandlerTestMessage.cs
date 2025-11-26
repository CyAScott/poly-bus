namespace PolyBus.Transport.Transactions.Messages.Handlers.Serializers;

[MessageInfo(MessageType.Command, "polybus", "json-handler-test-message", 1, 0, 0)]
class JsonHandlerTestMessage
{
    public required string Text { get; init; }
}
