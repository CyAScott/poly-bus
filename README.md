# PolyBus

<img src="PolyBus.png" height="100" width="100" />

**A polyglot messaging framework for building interoperable applications across multiple programming languages.**

PolyBus provides a unified interface for sending and receiving messages between applications written in different languages. Whether you're building microservices, distributed systems, or integrating legacy applications, PolyBus enables seamless communication across your polyglot stack.

## 🌟 Key Features

- **🔄 Multi-Language Support**: Native implementations for TypeScript, Python, .NET, and Kotlin
- **🚀 Flexible Transport**: Pluggable transport layer supporting various messaging systems
- **⚡ Async/Await**: Modern asynchronous APIs in all language implementations
- **🔌 Middleware Pipeline**: Extensible handler chains for incoming and outgoing messages
- **📦 Transaction Support**: Atomic message operations with commit/abort semantics
- **🎯 Type Safety**: Strong typing and interface definitions across all platforms
- **🛠️ Builder Pattern**: Fluent API for easy configuration
- **📝 Message Metadata**: Rich message headers and routing information
- **🔁 Serialization**: Built-in JSON serialization with customizable handlers
- **⚠️ Error Handling**: Comprehensive error handlers for reliable message processing

## 📋 Supported Languages

| Language | Version | Status | Package |
|----------|---------|--------|---------|
| **TypeScript/JavaScript** | Node.js 14+ | ✅ Stable | CommonJS, ESM, UMD |
| **Python** | 3.8-3.12 | ✅ Stable | PyPI package |
| **.NET** | .NET Standard 2.1 | ✅ Stable | NuGet package |
| **Kotlin** | JDK 17+ | ✅ Stable | Gradle/JVM package |
| **PHP** | 8.0+ | 🚧 Planned | - |

## 🚀 Quick Start

### TypeScript

```typescript
import { PolyBusBuilder, JsonHandlers } from 'poly-bus';

// Configure the bus
const builder = new PolyBusBuilder();
builder.name = 'my-service';

// Add JSON serialization
const jsonHandlers = new JsonHandlers();
builder.incomingHandlers.push(jsonHandlers.deserializer.bind(jsonHandlers));
builder.outgoingHandlers.push(jsonHandlers.serializer.bind(jsonHandlers));

// Build and start
const bus = await builder.build();
await bus.start();

// Send a message
const transaction = await bus.createOutgoingTransaction();
transaction.add({ type: 'UserCreated', userId: 123 });
await transaction.commit();

await bus.stop();
```

### Kotlin

```kotlin
import kotlinx.coroutines.runBlocking
import polybus.PolyBusBuilder
import polybus.transport.transactions.messages.MessageInfo
import polybus.transport.transactions.messages.MessageType
import polybus.transport.transactions.messages.handlers.serializers.JsonHandlers

@MessageInfo(MessageType.EVENT, "users", "user-created", 1, 0, 0)
data class UserCreated(val userId: Int)

fun main() = runBlocking {
    val builder = PolyBusBuilder()
    builder.name = "my-service"

    val jsonHandlers = JsonHandlers()
    builder.incomingPipeline.add(jsonHandlers::deserializer)
    builder.outgoingPipeline.add(jsonHandlers::serializer)
    builder.messages.add(UserCreated::class.java)

    val bus = builder.build()
    bus.start()

    val transaction = bus.createOutgoingTransaction()
    transaction.add(UserCreated(userId = 123))
    transaction.commit()

    bus.stop()
}
```

### Python

```python
from poly_bus import PolyBusBuilder, JsonHandlers

# Configure the bus
builder = PolyBusBuilder()
builder.name = 'my-service'

# Add JSON serialization
json_handlers = JsonHandlers()
builder.incoming_handlers.append(json_handlers.deserializer)
builder.outgoing_handlers.append(json_handlers.serializer)

# Build and start
bus = await builder.build()
await bus.start()

# Send a message
transaction = await bus.create_outgoing_transaction()
transaction.add({'type': 'UserCreated', 'user_id': 123})
await transaction.commit()

await bus.stop()
```

### .NET

```csharp
using PolyBus;
using PolyBus.Transport.Transactions.Messages.Handlers;

// Configure the bus
var builder = new PolyBusBuilder
{
    Name = "my-service"
};

// Add JSON serialization
var jsonHandlers = new JsonHandlers();
builder.IncomingHandlers.Add(jsonHandlers.Deserializer);
builder.OutgoingHandlers.Add(jsonHandlers.Serializer);

// Build and start
var bus = await builder.Build();
await bus.Start();

// Send a message
var transaction = await bus.CreateOutgoingTransaction();
transaction.Add(new { Type = "UserCreated", UserId = 123 });
await transaction.Commit();

await bus.Stop();
```

## 📚 Documentation

For comprehensive documentation, examples, and detailed guides, please visit the [**PolyBus Wiki**](https://github.com/CyAScott/poly-bus/wiki).

### Documentation Topics

- **[Getting Started Guide](https://github.com/CyAScott/poly-bus/wiki/Getting-Started)** - Installation and basic setup
- **[Core Concepts](https://github.com/CyAScott/poly-bus/wiki/Core-Concepts)** - Understanding transactions, handlers, and transports
- **[API Reference](https://github.com/CyAScott/poly-bus/wiki/API-Reference)** - Complete API documentation for all languages
- **[Transport Implementations](https://github.com/CyAScott/poly-bus/wiki/Transports)** - Available transports and custom transport development
- **[Handlers & Middleware](https://github.com/CyAScott/poly-bus/wiki/Handlers)** - Building custom handlers and middleware
- **[Message Serialization](https://github.com/CyAScott/poly-bus/wiki/Serialization)** - JSON, custom serializers, and content types
- **[Error Handling](https://github.com/CyAScott/poly-bus/wiki/Error-Handling)** - Error handlers and recovery strategies
- **[Advanced Topics](https://github.com/CyAScott/poly-bus/wiki/Advanced)** - Delayed messages, subscriptions, and patterns
- **[Examples](https://github.com/CyAScott/poly-bus/wiki/Examples)** - Real-world usage examples and patterns
- **[Migration Guides](https://github.com/CyAScott/poly-bus/wiki/Migration)** - Upgrading between versions

## 🏗️ Architecture

PolyBus follows a clean, layered architecture:

```
┌─────────────────────────────────────┐
│        Application Code             │
├─────────────────────────────────────┤
│          IPolyBus API               │
├─────────────────────────────────────┤
│     Handler Pipeline (Middleware)   │
│      ┌──────────┐  ┌──────────┐     │
│      │ Incoming │  │ Outgoing │     │
│      │ Handlers │  │ Handlers │     │
│      └──────────┘  └──────────┘     │
├─────────────────────────────────────┤
│      Transaction Management         │
├─────────────────────────────────────┤
│       Transport Interface           │
│    (ITransport abstraction)         │
├─────────────────────────────────────┤
│   Transport Implementations         │
│  (RabbitMQ, Kafka, SQS, etc.)       │
└─────────────────────────────────────┘
```

### Core Components

- **IPolyBus**: Main interface providing message send/receive operations
- **Transactions**: Atomic units of work for grouping related messages
- **Handlers**: Middleware pipeline for processing incoming/outgoing messages
- **Transport**: Pluggable abstraction for different messaging systems
- **Messages**: Strongly-typed message objects with metadata and headers
- **Builder**: Fluent API for configuration and dependency injection

## 🔌 Transport Support

PolyBus supports a pluggable transport architecture. Current and planned transports:

- ✅ **In-Memory Transport** - For testing and same-process communication
- 🚧 **RabbitMQ** - AMQP-based messaging
- 🚧 **Azure Service Bus** - Cloud-native messaging
- 🚧 **Amazon SQS** - AWS message queuing
- 🚧 **Apache Kafka** - Distributed streaming
- 🚧 **Redis Pub/Sub** - Lightweight messaging

Custom transports can be implemented by extending the `ITransport` interface.

## 🛠️ Development

Each language implementation has its own development setup:

### TypeScript Development

```bash
cd src/typescript
npm install
npm run build        # Build the project
npm test            # Run tests
npm run lint        # Check code quality
```

See [TypeScript README](src/typescript/README.md) for detailed development instructions.

### Python Development

```bash
cd src/python
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
./dev.sh install
./dev.sh test
./dev.sh lint
```

See [Python README](src/python/README.md) for detailed development instructions.

### .NET Development

```bash
cd src/dotnet
dotnet restore
dotnet build
dotnet test
./lint.sh
```

See [.NET README](src/dotnet/README.md) for detailed development instructions.

### Kotlin Development

```bash
cd src/kotlin
gradle clean
gradle build
gradle test
gradle coverage
```

See [Kotlin README](src/kotlin/README.md) for detailed development instructions.

## 🧪 Testing

All implementations include comprehensive test suites:

- **Unit Tests**: Testing individual components in isolation
- **Integration Tests**: Testing component interactions
- **Code Coverage**: Maintaining high coverage standards
- **Type Safety**: Static analysis and type checking

## 📦 Installation

### TypeScript/JavaScript

```bash
npm install poly-bus
# or
yarn add poly-bus
```

### Python

```bash
pip install poly-bus
```

### .NET

```bash
dotnet add package PolyBus
```

### Kotlin

```bash
cd src/kotlin
gradle build
```

For Kotlin package usage and publishing details, see [Kotlin README](src/kotlin/README.md).

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Code style and conventions
- Testing requirements
- Pull request process
- Development setup

### Releasing

This project uses automated semantic versioning and publishing. See:
- **[Quick Release Guide](RELEASE.md)** - Quick reference for developers
- **[Publishing Setup](PUBLISHING.md)** - Complete setup and troubleshooting guide
- **[Changelog](CHANGELOG.md)** - Version history

## 📄 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## 🔗 Links

- **Documentation**: [GitHub Wiki](https://github.com/CyAScott/poly-bus/wiki)
- **Issues**: [GitHub Issues](https://github.com/CyAScott/poly-bus/issues)
- **Discussions**: [GitHub Discussions](https://github.com/CyAScott/poly-bus/discussions)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

## ⭐ Project Status

PolyBus is actively maintained and production-ready for TypeScript, Python, .NET, and Kotlin implementations. PHP support is planned for future releases.

If you find PolyBus useful, please consider giving it a star ⭐ on GitHub!