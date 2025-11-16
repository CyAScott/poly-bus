# Jest Testing Setup for PolyBus TypeScript

This document describes the Jest testing setup for the PolyBus TypeScript project.

## Overview

Jest has been configured with full TypeScript support, ES modules, and code coverage reporting. The setup includes:

- **TypeScript Support**: Full compilation and type checking via `ts-jest`
- **ES Modules**: Native ESM support for modern JavaScript
- **Code Coverage**: Comprehensive coverage reporting with multiple output formats
- **Decorator Support**: Support for experimental decorators and metadata

## Available Test Scripts

| Script | Description |
|--------|-------------|
| `npm test` | Run all tests with coverage and enforce coverage thresholds |
| `npm run test:dev` | Run tests with coverage but without threshold enforcement (good for development) |
| `npm run test:watch` | Run tests in watch mode for development |
| `npm run test:coverage` | Run tests and generate detailed coverage reports |
| `npm run test:ci` | Run tests in CI mode (no watch, coverage required) |

## Test File Organization

Tests should be placed in one of these locations:

```
src/
  __tests__/           # Test files here
    *.test.ts         # Test files ending in .test.ts
    *.spec.ts         # Test files ending in .spec.ts
  component/
    component.test.ts  # Tests alongside source files
```

## Coverage Configuration

### Coverage Reports

Coverage reports are generated in multiple formats:

- **Console**: Text output during test runs
- **HTML**: Browse `coverage/lcov-report/index.html` for detailed reports
- **LCOV**: `coverage/lcov.info` for CI/CD integration
- **JSON**: `coverage/coverage-final.json` for programmatic access

### Coverage Thresholds

Current coverage thresholds (adjust in `jest.config.js`):

- **Statements**: 50%
- **Branches**: 50%
- **Functions**: 50%
- **Lines**: 50%

### Coverage Exclusions

The following files are excluded from coverage:

- Type definition files (`*.d.ts`)
- Test files (`*.test.ts`, `*.spec.ts`)
- Index files (often just re-exports)
- Template files (`*template*.ts`)

## Test Examples

### Basic Test Structure

```typescript
import { describe, it, expect } from '@jest/globals';
import { YourComponent } from '../your-component';

describe('YourComponent', () => {
  it('should create an instance', () => {
    const instance = new YourComponent();
    expect(instance).toBeDefined();
  });
});
```

### With Setup and Teardown

```typescript
import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';

describe('YourComponent', () => {
  let component: YourComponent;

  beforeEach(() => {
    component = new YourComponent();
  });

  afterEach(() => {
    // Cleanup if needed
  });

  it('should work correctly', () => {
    expect(component.someMethod()).toBe('expected result');
  });
});
```

### Mocking

```typescript
import { jest } from '@jest/globals';

// Mock a function
const mockFunction = jest.fn();
mockFunction.mockReturnValue('mocked value');

// Mock a module
jest.mock('../dependency', () => ({
  DependencyClass: jest.fn().mockImplementation(() => ({
    method: jest.fn().mockReturnValue('mocked')
  }))
}));
```

## Jest Configuration

The Jest configuration is in `jest.config.js` and includes:

- **Preset**: `ts-jest/presets/default-esm` for ES modules
- **Test Environment**: Node.js
- **Transform**: TypeScript compilation with decorators
- **Module Resolution**: Support for ES module imports
- **Setup**: Global test configuration in `jest.setup.js`

## Tips for Writing Tests

1. **Use descriptive test names**: `it('should return error when input is invalid')`
2. **Group related tests**: Use `describe` blocks to organize tests
3. **Test edge cases**: Include tests for error conditions and boundary values
4. **Keep tests focused**: Each test should verify one specific behavior
5. **Use appropriate matchers**: Choose the most specific Jest matcher for clarity

## Common Jest Matchers

```typescript
// Equality
expect(value).toBe(expected);           // Strict equality (===)
expect(value).toEqual(expected);        // Deep equality

// Truthiness
expect(value).toBeTruthy();
expect(value).toBeFalsy();
expect(value).toBeNull();
expect(value).toBeUndefined();
expect(value).toBeDefined();

// Numbers
expect(value).toBeGreaterThan(3);
expect(value).toBeCloseTo(0.3);

// Strings
expect(string).toMatch(/pattern/);
expect(string).toContain('substring');

// Arrays and Objects
expect(array).toContain(item);
expect(object).toHaveProperty('key');
expect(array).toHaveLength(3);

// Functions
expect(fn).toThrow();
expect(fn).toHaveBeenCalled();
expect(fn).toHaveBeenCalledWith(args);
```

## Next Steps

1. **Start testing**: Use the provided template in `src/__tests__/test-template.ts`
2. **Add more tests**: Focus on your core business logic first
3. **Increase coverage**: Aim to gradually increase coverage thresholds
4. **CI Integration**: Use `npm run test:ci` in your CI/CD pipeline

## Troubleshooting

### Common Issues

1. **ES Module errors**: Ensure imports use `.js` extensions in test files if needed
2. **Decorator errors**: Check that `experimentalDecorators` is enabled
3. **Coverage issues**: Verify file paths in `collectCoverageFrom` configuration
4. **Type errors**: Ensure `@types/jest` is installed and imported correctly

### Getting Help

- Check the [Jest documentation](https://jestjs.io/docs/getting-started)
- Review the [ts-jest documentation](https://kulshekhar.github.io/ts-jest/)
- Examine existing test files for patterns and examples