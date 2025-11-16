# GitHub Copilot Instructions for PolyBus

## Project Overview

PolyBus is a **polyglot messaging framework** that enables seamless communication between applications written in different programming languages. It provides unified interfaces across TypeScript, Python, and .NET (with PHP planned) for building interoperable distributed systems and microservices.

## Core Architecture Principles

### Layered Architecture
```
Application Code → IPolyBus API → Handler Pipeline → Transaction Management → Transport Interface → Transport Implementations
```

### Key Components
1. **IPolyBus**: Main interface for message send/receive operations
2. **Transactions**: Atomic units grouping related messages with commit/abort semantics
3. **Handlers**: Middleware pipeline for incoming/outgoing message processing
4. **Transport**: Pluggable abstraction for messaging systems (RabbitMQ, Kafka, etc.)
5. **Messages**: Strongly-typed objects with metadata and headers
6. **Builder**: Fluent API for configuration

## Language-Specific Guidelines

### TypeScript (`src/typescript/`)

**Technology Stack:**
- Node.js 14+, TypeScript 5.2+
- Jest for testing, ESLint for linting
- Rollup for browser bundling, supports CommonJS, ESM, UMD

**Coding Conventions:**
- Use async/await for all asynchronous operations
- Implement interfaces with `implements` keyword
- Use `reflect-metadata` for decorator metadata
- Export types and interfaces alongside implementations
- Prefer functional programming patterns where appropriate
- Use descriptive variable names (e.g., `transaction`, not `tx`)

**Testing:**
- Place tests in `__tests__` directories next to source files
- Name test files: `*.test.ts`
- Use `@jest/globals` for test functions
- Mock async operations appropriately
- Maintain high coverage (run `npm test:coverage`)

**Build System:**
- Source: `src/`, Output: `dist/`
- Multiple targets: CommonJS (`dist/index.js`), ESM (`dist/index.mjs`), UMD (`dist/index.umd.js`)
- Type definitions: `dist/index.d.ts`

### Python (`src/python/`)

**Technology Stack:**
- Python 3.8-3.12
- pytest, pytest-asyncio, pytest-cov for testing
- black, isort, flake8, mypy for code quality
- setuptools for packaging

**Coding Conventions:**
- Use type hints everywhere (enforced by mypy strict mode)
- Follow PEP 8 style guide (enforced by black/isort)
- Use `async`/`await` for asynchronous operations
- Implement abstract base classes with `ABC` and `@abstractmethod`
- Use snake_case for variables/functions, PascalCase for classes
- Document with docstrings (Google/NumPy style)

**Type Safety:**
```python
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional

class IPolyBus(ABC):
    @abstractmethod
    async def start(self) -> None:
        """Start the bus."""
        pass
```

**Testing:**
- Place tests in `tests/` directory (mirrors `src/` structure)
- Name test files: `test_*.py`
- Use `pytest.mark.asyncio` for async tests
- Coverage config excludes interfaces, handlers, factories, and `__init__.py`

**Development:**
- Use `./dev.sh` script for common tasks (install, test, lint, format)
- Virtual environment recommended

### .NET (`src/dotnet/`)

**Technology Stack:**
- .NET Standard 2.1 (cross-platform)
- xUnit or NUnit for testing
- Solution: `PolyBus.slnx`
- Projects: `PolyBus/` (library), `PloyBus.Tests/` (tests)

**Coding Conventions:**
- Use PascalCase for public members, camelCase for private
- Implement interfaces explicitly: `public class PolyBus : IPolyBus`
- Use `async`/`await` with `Task<T>` return types
- Properties over fields for public APIs
- Use expression bodies for simple members
- Leverage C# modern features (pattern matching, null-coalescing, etc.)

**Testing:**
- Test project: `PloyBus.Tests/`
- Use async test methods
- Run: `dotnet test`

**Linting:**
- Use `./lint.sh` for code quality checks
- Follow `.editorconfig` and `.DotSettings` conventions

## Cross-Language Consistency

### Naming Conventions
Maintain equivalent naming across languages:

| Concept | TypeScript | Python | .NET |
|---------|-----------|--------|------|
| Interface | `IPolyBus` | `IPolyBus` (ABC) | `IPolyBus` |
| Builder | `PolyBusBuilder` | `PolyBusBuilder` | `PolyBusBuilder` |
| Methods | `createTransaction()` | `create_transaction()` | `CreateTransaction()` |
| Properties | `incomingHandlers` | `incoming_handlers` | `IncomingHandlers` |

### API Parity
All implementations must support:
- Same core interfaces and methods
- Async/await patterns
- Transaction commit/abort semantics
- Handler pipeline architecture
- Message metadata and headers
- Transport abstraction
- Builder pattern for configuration

### Message Format
Messages are JSON-serializable with this structure:
```json
{
  "type": "MessageType",
  "data": {},
  "headers": {
    "messageId": "uuid",
    "correlationId": "uuid",
    "contentType": "application/json"
  }
}
```

## Handler Pipeline Pattern

Handlers are middleware functions that process messages:

**TypeScript:**
```typescript
type IncomingHandler = (message: IncomingMessage, next: () => Promise<void>) => Promise<void>;
type OutgoingHandler = (message: Message, next: () => Promise<void>) => Promise<void>;
```

**Python:**
```python
IncomingHandler = Callable[[IncomingMessage, Callable[[], Awaitable[None]]], Awaitable[None]]
OutgoingHandler = Callable[[Message, Callable[[], Awaitable[None]]], Awaitable[None]]
```

**.NET:**
```csharp
public delegate Task IncomingHandler(IncomingMessage message, Func<Task> next);
public delegate Task OutgoingHandler(Message message, Func<Task> next);
```

**Handler Order:**
- Handlers execute in order they're added
- Each handler calls `next()` to continue the pipeline
- Error handlers wrap the pipeline for exception handling

## Transport Interface

Transports must implement these core methods across all languages:

**Key Methods:**
- `start()` / `Start()` - Initialize the transport
- `stop()` / `Stop()` - Shutdown the transport
- `send(message)` / `Send(message)` - Send a message
- `createTransaction()` / `CreateTransaction()` - Begin a transaction
- `subscribe(handler)` / `Subscribe(handler)` - Register message handler

**In-Memory Transport:**
- Default transport for testing
- Simulates message passing without external dependencies
- Located in `transport/in-memory/` directory

## Common Patterns

### Transaction Pattern
```typescript
const transaction = await bus.createTransaction();
try {
    transaction.addOutgoingMessage({ type: 'Event', data: {} });
    await transaction.commit();
} catch (error) {
    await transaction.abort();
}
```

### Builder Pattern
```typescript
const builder = new PolyBusBuilder();
builder.name = 'my-service';
builder.incomingHandlers.push(deserializer);
builder.outgoingHandlers.push(serializer);
const bus = await builder.build();
```

### Serialization
```typescript
const jsonHandlers = new JsonHandlers();
builder.incomingHandlers.push(jsonHandlers.deserializer.bind(jsonHandlers));
builder.outgoingHandlers.push(jsonHandlers.serializer.bind(jsonHandlers));
```

## Error Handling

### Error Handler Types
1. **Transaction Errors**: Handle errors during message processing
2. **Transport Errors**: Handle connection/send failures
3. **Serialization Errors**: Handle JSON parse/stringify failures

### Implementation
Error handlers wrap the pipeline and provide:
- Retry logic
- Logging
- Dead-letter queuing
- Circuit breaker patterns

## Testing Guidelines

### Unit Tests
- Test individual components in isolation
- Mock dependencies (especially transport)
- Test error conditions and edge cases
- Verify handler pipeline execution order

### Integration Tests
- Test component interactions
- Use in-memory transport for deterministic tests
- Test full message flow (send → receive → process)
- Verify transaction semantics (commit/abort)

### Coverage Goals
- Aim for >90% code coverage
- All public APIs must have tests
- Critical paths require multiple test scenarios
- Exclude interface definitions and simple delegators

## Documentation Standards

### Code Comments
- Document public APIs with JSDoc/docstrings/XML comments
- Explain "why" not "what" in implementation comments
- Include usage examples for complex APIs
- Note cross-language compatibility requirements

### README Files
- Each language has its own README in `src/{language}/`
- Include quickstart examples
- Document development setup
- List language-specific considerations

### Examples
- Place examples in `src/{language}/examples/`
- Show common use cases
- Demonstrate best practices
- Keep examples simple and focused

## Code Review Checklist

When generating code:
- [ ] Follows language-specific naming conventions
- [ ] Uses async/await appropriately
- [ ] Includes error handling
- [ ] Has type annotations (TypeScript/Python) or strong typing (.NET)
- [ ] Maintains API parity with other languages
- [ ] Includes relevant tests
- [ ] Follows DRY principle
- [ ] Handles edge cases
- [ ] Documents public APIs
- [ ] Uses appropriate design patterns

## Performance Considerations

- **Async Operations**: All I/O must be asynchronous
- **Handler Pipeline**: Keep handlers lightweight, avoid blocking
- **Message Size**: Be mindful of large payloads
- **Connection Pooling**: Transport implementations should pool connections
- **Memory Management**: Dispose resources properly in all languages

## Security Considerations

- **Message Validation**: Validate incoming messages
- **Serialization**: Prevent injection attacks in JSON handlers
- **Transport Security**: Support TLS/SSL in transport implementations
- **Authentication**: Support auth mechanisms in transports
- **Authorization**: Provide hooks for message-level authorization

## Future Considerations

### PHP Implementation (`src/php/`)
- PHP 8.0+ with type declarations
- PSR-4 autoloading, PSR-12 coding standards
- Composer for dependency management
- PHPUnit for testing
- Async support via Amphp or ReactPHP

### Additional Transports
- RabbitMQ (AMQP)
- Azure Service Bus
- Amazon SQS
- Apache Kafka
- Redis Pub/Sub

## Common Commands

### TypeScript
```bash
cd src/typescript
npm install          # Install dependencies
npm run build        # Build all targets
npm test             # Run tests
npm run test:coverage # Coverage report
npm run lint         # Check code quality
npm run lint:fix     # Auto-fix linting issues
```

### Python
```bash
cd src/python
./dev.sh install     # Setup virtual env and install
./dev.sh test        # Run tests with coverage
./dev.sh lint        # Check code quality
./dev.sh format      # Format code (black/isort)
./dev.sh type-check  # Run mypy
```

### .NET
```bash
cd src/dotnet
dotnet restore       # Restore dependencies
dotnet build         # Build solution
dotnet test          # Run tests
./lint.sh            # Run linting
```

## Resources

- **Main README**: `/README.md`
- **Contributing Guide**: `/CONTRIBUTING.md` (if exists)
- **Documentation**: GitHub Wiki (planned)
- **Language READMEs**: `src/{language}/README.md`

## When in Doubt

1. **Consistency First**: Match existing patterns in the codebase
2. **Check Other Languages**: See how feature is implemented in other languages
3. **Test Everything**: Write tests before/during implementation
4. **Document APIs**: All public interfaces need documentation
5. **Ask Questions**: Better to clarify than implement incorrectly
