# PolyBus .NET

A .NET implementation of the PolyBus messaging library, providing a unified interface for message transport across different messaging systems.

## Prerequisites

- [.NET 10.0 SDK](https://dotnet.microsoft.com/download/dotnet/10.0) or later
- Any IDE that supports .NET development (Visual Studio, VS Code, JetBrains Rider)

## Project Structure

```
src/dotnet/
├── PolyBus/                    # Main library project
│   ├── PolyBus.csproj          # Project file
│   ├── IPolyBus.cs             # Main interface
│   ├── PolyBus.cs              # Core implementation
│   ├── PolyBusBuilder.cs       # Builder pattern implementation
│   ├── Headers.cs              # Message headers
│   └── Transport/              # Transport implementations
│       ├── ITransport.cs       # Transport interface
│       └── TransportFactory.cs
├── PloyBus.Tests/              # Test project
│   ├── PloyBus.Tests.csproj    # Test project file
│   └── PolyBusTests.cs         # Test implementations
├── Directory.Build.props       # Common build properties
├── PolyBus.slnx                # Solution file
└── lint.sh                     # Code quality script
```

## Quick Start

### Building the Project

```bash
# Navigate to the dotnet directory
cd src/dotnet

# Restore dependencies
dotnet restore

# Build the solution
dotnet build
```

### Running Tests

```bash
# Run all tests
dotnet test

# Run tests with detailed output
dotnet test --verbosity normal

# Run tests with code coverage (if coverage tools are installed)
dotnet test --collect:"XPlat Code Coverage"
```

### Running Specific Test Projects

```bash
# Run only the main test project
dotnet test PloyBus.Tests/PloyBus.Tests.csproj

# Run tests matching a specific pattern
dotnet test --filter "TestMethodName"
```

## Development Workflow

### Code Quality and Linting

This project includes comprehensive code analysis and formatting tools:

```bash
# Run the complete linting suite
./lint.sh

# Check code formatting only
dotnet format --verify-no-changes

# Auto-fix formatting issues
dotnet format

# Build with analysis enabled
dotnet build --verbosity normal
```

### IDE Integration

#### Visual Studio Code
1. Install the C# extension
2. Open the `src/dotnet` folder in VS Code
3. Analysis warnings will appear in the Problems panel
4. Use Ctrl+. for quick fixes

#### Visual Studio / JetBrains Rider
1. Open `PolyBus.slnx` solution file
2. Analysis results appear in Error List / Inspection Results
3. Follow suggested fixes and refactorings

## Configuration

### Build Configuration

The project uses `Directory.Build.props` for common settings:

- **Target Framework**: .NET 10.0
- **Code Analysis**: Enabled with recommended rules
- **Nullable Reference Types**: Enabled
- **Documentation Generation**: Enabled
- **Implicit Usings**: Enabled

### Code Style

Code style is enforced through:
- Microsoft.CodeAnalysis.NetAnalyzers
- EditorConfig settings (see [LINTING.md](LINTING.md))
- Built-in .NET formatting rules

## Dependencies

### Main Project (PolyBus)
- `Microsoft.Extensions.Logging.Abstractions` (9.0.10)

### Test Project (PloyBus.Tests)
- `Microsoft.NET.Test.Sdk` (18.0.0)
- `NUnit` (4.4.0)
- `NUnit.Analyzers` (4.11.2)
- `NUnit3TestAdapter` (5.2.0)

## Common Commands

```bash
# Clean build artifacts
dotnet clean

# Restore packages
dotnet restore

# Build without restore
dotnet build --no-restore

# Run tests with logger
dotnet test --logger "console;verbosity=detailed"

# Pack for NuGet (when ready for distribution)
dotnet pack --configuration Release

# Watch for changes and rebuild
dotnet watch build

# Watch for changes and rerun tests
dotnet watch test
```

## Troubleshooting

### Build Issues

1. **Missing SDK**: Ensure .NET 10.0 SDK is installed
   ```bash
   dotnet --version
   ```

2. **Package Restore Issues**: Clear NuGet cache
   ```bash
   dotnet nuget locals all --clear
   dotnet restore
   ```

3. **Analysis Warnings**: See [LINTING.md](LINTING.md) for details on addressing code analysis warnings

### Test Issues

1. **Tests Not Discovering**: Ensure test project references are correct
2. **NUnit Issues**: Verify NUnit packages are properly restored

## Contributing

1. Follow the established code style (enforced by analyzers)
2. Run `./lint.sh` before committing
3. Ensure all tests pass: `dotnet test`
4. Add tests for new functionality
5. Update documentation as needed

## Additional Resources

- [LINTING.md](LINTING.md) - Detailed information about code quality setup
- [.NET Documentation](https://docs.microsoft.com/en-us/dotnet/)
- [NUnit Documentation](https://docs.nunit.org/)

## License

See the main project LICENSE file for licensing information.