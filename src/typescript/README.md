# PolyBus TypeScript

A TypeScript implementation of the PolyBus messaging library, providing a unified interface for message transport across different messaging systems. This package is designed to work seamlessly in both Node.js and browser environments.

## Prerequisites

- [Node.js 14.0+](https://nodejs.org/) (tested with Node.js 14-20)
- npm or yarn package manager
- Any IDE that supports TypeScript development (VS Code, WebStorm, etc.)

## Project Structure

```
src/typescript/
├── src/                        # Source code
│   ├── index.ts                # Main entry point
│   ├── i-poly-bus.ts           # Main interface
│   ├── poly-bus.ts             # Core implementation
│   ├── poly-bus-builder.ts     # Builder pattern implementation
│   ├── headers.ts              # Message headers
│   ├── transport/              # Transport implementations
│   │   ├── i-transport.ts      # Transport interface
│   │   └── ...
│   └── __tests__/              # Test files
│       ├── poly-bus.test.ts    # Test implementations
│       └── headers.test.ts
├── dist/                       # Compiled output
│   ├── index.js                # CommonJS build
│   ├── index.mjs               # ES Module build
│   ├── index.umd.js            # UMD build (browser)
│   └── index.d.ts              # TypeScript declarations
├── package.json                # Project configuration and dependencies
├── tsconfig.json               # TypeScript configuration
├── jest.config.js              # Jest testing configuration
├── eslint.config.js            # ESLint configuration
├── rollup.config.js            # Rollup bundler configuration
└── README.md                   # This file
```

## Quick Start

### Installing Dependencies

```bash
# Navigate to the typescript directory
cd src/typescript

# Install dependencies
npm install
# Or with yarn:
yarn install
```

### Building the Project

```bash
# Build all formats (CommonJS, ESM, UMD, types)
npm run build

# Build and watch for changes
npm run dev

# Clean build artifacts
npm run clean
```

### Running Tests

```bash
# Run all tests
npm test
# Or: npm run test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run tests for CI/CD
npm run test:ci
```

## Development Workflow

### Code Quality and Linting

This project includes comprehensive code analysis and formatting tools:

```bash
# Run ESLint to check code quality
npm run lint

# Auto-fix linting issues
npm run lint:fix

# TypeScript type checking is performed during build
npm run build
```

### IDE Integration

#### Visual Studio Code
1. Install the ESLint extension
2. Install the TypeScript extension (usually built-in)
3. Open the `src/typescript` folder in VS Code
4. Auto-formatting and linting will work automatically

#### WebStorm / IntelliJ IDEA
1. Open the `src/typescript` folder as a project
2. Enable ESLint integration (Settings → Languages & Frameworks → JavaScript → Code Quality Tools → ESLint)
3. TypeScript support is built-in

## Configuration

### Package Configuration

The project uses modern TypeScript packaging with dual module support:

- **Target**: ES2018
- **Module Formats**: CommonJS, ESM, UMD (browser)
- **Node Version**: 14.0+
- **Type Safety**: Strict mode enabled
- **Decorators**: Experimental decorators enabled

### Build Outputs

The package exports multiple formats for maximum compatibility:

```javascript
{
  "main": "./dist/index.js",        // CommonJS for Node.js
  "module": "./dist/index.mjs",     // ES Module for bundlers
  "browser": "./dist/index.umd.js", // UMD for browsers
  "types": "./dist/index.d.ts"      // TypeScript definitions
}
```

### Code Style

Code style is enforced through:
- **ESLint** with TypeScript plugin
- **TypeScript** strict mode
- Consistent formatting rules (2-space indentation, single quotes, semicolons)

### Testing Configuration

Jest configuration includes:
- **Test Environment**: Node.js
- **Preset**: ts-jest with ESM support
- **Coverage**: HTML, LCOV, JSON, text reports
- **Coverage Thresholds**: 50% for branches, functions, lines, statements
- **Test Discovery**: `**/*.test.ts`, `**/*.spec.ts`

## Dependencies

### Runtime Dependencies
- `reflect-metadata` (^0.2.2) - Metadata reflection for decorators

### Development Dependencies
- `typescript` (^5.2.2) - TypeScript compiler
- `jest` (^30.2.0) - Testing framework
- `ts-jest` (^29.4.5) - TypeScript support for Jest
- `eslint` (^9.39.0) - Code linting
- `@typescript-eslint/eslint-plugin` (^8.46.2) - TypeScript ESLint rules
- `rollup` (^4.1.4) - Module bundler
- `@rollup/plugin-typescript` (^11.1.5) - Rollup TypeScript plugin
- `@types/node` (^20.8.0) - Node.js type definitions
- `@types/jest` (^30.0.0) - Jest type definitions

## Common Commands

```bash
# Development
npm install              # Install dependencies
npm run build            # Build all formats
npm run dev              # Build and watch for changes
npm run clean            # Clean build artifacts

# Testing
npm test                 # Run tests once
npm run test:watch       # Run tests in watch mode
npm run test:coverage    # Run tests with coverage report
npm run test:dev         # Run tests without thresholds (for development)

# Code Quality
npm run lint             # Check code with ESLint
npm run lint:fix         # Auto-fix linting issues

# Package Management
npm run prepublishOnly   # Clean and build (runs before npm publish)
```

## Troubleshooting

### Build Issues

1. **TypeScript Errors**: Check your TypeScript version
   ```bash
   npx tsc --version
   ```

2. **Module Resolution Issues**: Clear node_modules and reinstall
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Build Cache Issues**: Clean and rebuild
   ```bash
   npm run clean
   npm run build
   ```

### Test Issues

1. **Jest Configuration**: Ensure Jest and ts-jest are properly installed
   ```bash
   npm install --save-dev jest ts-jest @types/jest
   ```

2. **ES Module Issues**: Check that `"type": "module"` is in package.json

3. **Coverage Threshold Errors**: Use `test:dev` during development to bypass thresholds
   ```bash
   npm run test:dev
   ```

### Linting Issues

1. **ESLint Errors**: Auto-fix where possible
   ```bash
   npm run lint:fix
   ```

2. **TypeScript Strict Mode**: The project uses strict mode; add proper type annotations

## Using the Package

### In Node.js (CommonJS)

```javascript
const { PolyBus } = require('poly-bus');

const bus = new PolyBus();
// Use the bus...
```

### In Node.js (ES Modules)

```javascript
import { PolyBus } from 'poly-bus';

const bus = new PolyBus();
// Use the bus...
```

### In Browser (with bundler)

```javascript
import { PolyBus } from 'poly-bus';

const bus = new PolyBus();
// Use the bus...
```

### In Browser (UMD script tag)

```html
<script src="path/to/poly-bus/dist/index.umd.js"></script>
<script>
  const bus = new PolyBus.PolyBus();
  // Use the bus...
</script>
```

## Contributing

1. Follow the established code style (enforced by ESLint)
2. Run `npm run lint:fix` before committing
3. Ensure all tests pass: `npm test`
4. Maintain or improve code coverage
5. Add tests for new functionality
6. Add JSDoc comments for public APIs
7. Update TypeScript types as needed
8. Update documentation as needed

## Coverage Reports

After running tests with coverage (`npm run test:coverage`):
- **Terminal**: Coverage summary displayed in terminal
- **HTML**: Detailed report available in `coverage/index.html`
- **LCOV**: Machine-readable report in `coverage/lcov.info`
- **JSON**: Detailed JSON report in `coverage/coverage-final.json`

## Additional Resources

- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [ESLint Documentation](https://eslint.org/docs/latest/)
- [Rollup Documentation](https://rollupjs.org/guide/en/)
- [TESTING.md](TESTING.md) - Detailed testing guide

## License

See the main project LICENSE file for licensing information.
