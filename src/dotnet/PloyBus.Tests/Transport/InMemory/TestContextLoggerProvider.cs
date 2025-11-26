using System.Diagnostics;
using Microsoft.Extensions.Logging;

namespace PolyBus.Transport.InMemory;

[DebuggerStepThrough]
class TestContextLoggerProvider : ILoggerProvider
{
    public ILogger CreateLogger(string categoryName) => new TestContextLogger(categoryName);

    public void Dispose()
    {
    }
}
