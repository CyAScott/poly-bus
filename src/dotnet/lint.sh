#!/bin/bash

# .NET Code Linting Script
# This script runs various code analysis and linting checks for the .NET projects

echo "🔍 Running .NET Code Analysis..."
echo "======================================"

# Change to the dotnet source directory
cd "$(dirname "$0")"

# Build the solution with analysis enabled
echo ""
echo "📦 Building solution with code analysis..."
dotnet build --verbosity quiet --no-restore

if [ $? -eq 0 ]; then
    echo "✅ Build completed successfully with analysis warnings"
else
    echo "❌ Build failed - please check errors above"
    exit 1
fi

# Run code format check
echo ""
echo "🎨 Checking code formatting..."
dotnet format --verify-no-changes --verbosity diagnostic

if [ $? -eq 0 ]; then
    echo "✅ Code formatting is correct"
else
    echo "⚠️  Code formatting issues found - run 'dotnet format' to fix"
fi

# Run security analysis (if available)
echo ""
echo "🔒 Running security analysis..."
if command -v dotnet-security-scan &> /dev/null; then
    dotnet security-scan
else
    echo "ℹ️  Security scanner not installed - install with: dotnet tool install --global security-scan"
fi

echo ""
echo "🏁 Code analysis complete!"
echo "To fix formatting issues, run: dotnet format"
echo "To view analysis results in VS Code, check the Problems panel"