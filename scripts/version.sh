#!/usr/bin/env bash

# Version Management Script for PolyBus
# This script helps sync versions across all package configurations

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Files to update
TYPESCRIPT_PACKAGE="$ROOT_DIR/src/typescript/package.json"
PYTHON_PYPROJECT="$ROOT_DIR/src/python/pyproject.toml"
DOTNET_CSPROJ="$ROOT_DIR/src/dotnet/PolyBus/PolyBus.csproj"

print_usage() {
    echo "Usage: $0 [command] [version]"
    echo ""
    echo "Commands:"
    echo "  get                    - Display current versions"
    echo "  set <version>          - Set version across all packages"
    echo "  check                  - Check if all versions are in sync"
    echo "  bump <major|minor|patch> - Bump version by type"
    echo ""
    echo "Examples:"
    echo "  $0 get"
    echo "  $0 set 1.2.3"
    echo "  $0 bump minor"
    echo "  $0 check"
}

get_typescript_version() {
    if [ -f "$TYPESCRIPT_PACKAGE" ]; then
        grep -o '"version": "[^"]*"' "$TYPESCRIPT_PACKAGE" | cut -d'"' -f4
    else
        echo "N/A"
    fi
}

get_python_version() {
    if [ -f "$PYTHON_PYPROJECT" ]; then
        grep '^version = ' "$PYTHON_PYPROJECT" | cut -d'"' -f2
    else
        echo "N/A"
    fi
}

get_dotnet_version() {
    if [ -f "$DOTNET_CSPROJ" ]; then
        grep '<Version>' "$DOTNET_CSPROJ" | sed 's/.*<Version>\(.*\)<\/Version>.*/\1/' | tr -d ' '
    else
        echo "N/A"
    fi
}

display_versions() {
    echo -e "${BLUE}Current Package Versions:${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "TypeScript: ${GREEN}$(get_typescript_version)${NC}"
    echo -e "Python:     ${GREEN}$(get_python_version)${NC}"
    echo -e ".NET:       ${GREEN}$(get_dotnet_version)${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

check_versions_sync() {
    TS_VERSION=$(get_typescript_version)
    PY_VERSION=$(get_python_version)
    NET_VERSION=$(get_dotnet_version)
    
    if [ "$TS_VERSION" = "$PY_VERSION" ] && [ "$PY_VERSION" = "$NET_VERSION" ]; then
        echo -e "${GREEN}✓ All versions are in sync: ${TS_VERSION}${NC}"
        return 0
    else
        echo -e "${RED}✗ Versions are out of sync!${NC}"
        display_versions
        return 1
    fi
}

validate_semver() {
    local version=$1
    if [[ ! $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo -e "${RED}Error: Invalid semantic version format. Expected: X.Y.Z${NC}"
        return 1
    fi
    return 0
}

set_version() {
    local version=$1
    
    if ! validate_semver "$version"; then
        exit 1
    fi
    
    echo -e "${BLUE}Setting version to ${version} across all packages...${NC}"
    echo ""
    
    # Update TypeScript package.json
    if [ -f "$TYPESCRIPT_PACKAGE" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/\"version\": \"[^\"]*\"/\"version\": \"${version}\"/" "$TYPESCRIPT_PACKAGE"
        else
            # Linux
            sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"${version}\"/" "$TYPESCRIPT_PACKAGE"
        fi
        echo -e "${GREEN}✓ Updated TypeScript package.json${NC}"
    fi
    
    # Update Python pyproject.toml
    if [ -f "$PYTHON_PYPROJECT" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/^version = .*/version = \"${version}\"/" "$PYTHON_PYPROJECT"
        else
            sed -i "s/^version = .*/version = \"${version}\"/" "$PYTHON_PYPROJECT"
        fi
        echo -e "${GREEN}✓ Updated Python pyproject.toml${NC}"
    fi
    
    # Update .NET csproj
    if [ -f "$DOTNET_CSPROJ" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|<Version>.*</Version>|<Version>${version}</Version>|" "$DOTNET_CSPROJ"
        else
            sed -i "s|<Version>.*</Version>|<Version>${version}</Version>|" "$DOTNET_CSPROJ"
        fi
        echo -e "${GREEN}✓ Updated .NET PolyBus.csproj${NC}"
    fi
    
    echo ""
    display_versions
}

bump_version() {
    local bump_type=$1
    local current_version=$(get_typescript_version)
    
    if [ "$current_version" = "N/A" ]; then
        echo -e "${RED}Error: Cannot determine current version${NC}"
        exit 1
    fi
    
    IFS='.' read -r -a version_parts <<< "$current_version"
    local major="${version_parts[0]}"
    local minor="${version_parts[1]}"
    local patch="${version_parts[2]}"
    
    case $bump_type in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
        *)
            echo -e "${RED}Error: Invalid bump type. Use: major, minor, or patch${NC}"
            exit 1
            ;;
    esac
    
    local new_version="${major}.${minor}.${patch}"
    echo -e "${YELLOW}Bumping ${bump_type} version: ${current_version} → ${new_version}${NC}"
    echo ""
    
    set_version "$new_version"
}

# Main script logic
case "${1:-}" in
    get)
        display_versions
        ;;
    set)
        if [ -z "${2:-}" ]; then
            echo -e "${RED}Error: Version argument required${NC}"
            print_usage
            exit 1
        fi
        set_version "$2"
        ;;
    check)
        check_versions_sync
        ;;
    bump)
        if [ -z "${2:-}" ]; then
            echo -e "${RED}Error: Bump type required (major|minor|patch)${NC}"
            print_usage
            exit 1
        fi
        bump_version "$2"
        ;;
    help|--help|-h)
        print_usage
        ;;
    *)
        echo -e "${RED}Error: Invalid command${NC}"
        echo ""
        print_usage
        exit 1
        ;;
esac
