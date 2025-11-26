using Microsoft.Extensions.Logging;
using PolyBus.Transport.Transactions.Messages.Handlers.Serializers;

namespace PolyBus.Transport.InMemory;

class TestEnvironment
{
    public ILoggerFactory LoggerFactory { get; } = Microsoft.Extensions.Logging.LoggerFactory.Create(builder =>
    {
        builder.AddProvider(new TestContextLoggerProvider());
    });
    public InMemoryMessageBroker InMemoryMessageBroker { get; } = new();
    public TestEndpoint Alpha { get; } = new();
    public TestEndpoint Beta { get; } = new();
    public async Task Setup()
    {
        await SetupEndpoint(Alpha, "alpha");
        await SetupEndpoint(Beta, "beta");
    }

    async Task SetupEndpoint(TestEndpoint testEndpoint, string name)
    {
        var jsonHandlers = new JsonHandlers();

        // add handlers for incoming messages
        testEndpoint.Builder.IncomingPipeline.Add(jsonHandlers.Deserializer);
        testEndpoint.Builder.IncomingPipeline.Add(testEndpoint.Handler);

        // add messages
        testEndpoint.Builder.Messages.Add(typeof(AlphaCommand));
        testEndpoint.Builder.Messages.Add(typeof(AlphaEvent));
        testEndpoint.Builder.Name = name;

        // add handlers for outgoing messages
        testEndpoint.Builder.OutgoingPipeline.Add(jsonHandlers.Serializer);

        // configure InMemory transport
        testEndpoint.Builder.TransportFactory = InMemoryMessageBroker.AddEndpoint;
        InMemoryMessageBroker.Log = LoggerFactory.CreateLogger<InMemoryMessageBroker>();

        // create the bus instance
        testEndpoint.Bus = await testEndpoint.Builder.Build();
    }

    public async Task Start()
    {
        await Alpha.Bus.Start();
        await Beta.Bus.Start();
    }

    public async Task Stop()
    {
        await Alpha.Bus.Stop();
        await Beta.Bus.Stop();
    }
}
