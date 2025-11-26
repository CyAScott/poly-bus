using System.Diagnostics;
using Microsoft.Extensions.Logging;
using NUnit.Framework;

namespace PolyBus.Transport.InMemory;

[DebuggerStepThrough]
class TestContextLogger(string categoryName) : ILogger
{
    public IDisposable? BeginScope<TState>(TState state)
        where TState : notnull
        => null;

    public bool IsEnabled(LogLevel logLevel) => true;

    public void Log<TState>(LogLevel logLevel, EventId eventId, TState state, Exception? exception, Func<TState, Exception?, string> formatter)
    {
        TestContext.Out.WriteLine($"{DateTime.UtcNow:HH:mm:ss.fff} [{logLevel}] {categoryName}: {formatter(state, exception)}");
        if (exception != null)
        {
            TestContext.Out.WriteLine(exception);
        }
    }
}
