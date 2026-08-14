#!/bin/bash
# validate-kit-install.sh v0.4.0
# Validates kit installation: placeholders, paths, permissions, hooks

set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

ISSUES_FOUND=0
CRITICAL_ERRORS=0

# === HELPERS ===

log_section() {
    echo -e "${BLUE}$1${NC}"
}

log_ok() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((ISSUES_FOUND++))
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    ((ISSUES_FOUND++))
}

log_critical() {
    echo -e "${RED}[CRITICAL] $1${NC}"
    ((CRITICAL_ERRORS++))
}

# === VALIDATIONS ===

validate_placeholders() {
    log_section "📋 PLACEHOLDERS NÃO-RESOLVIDOS"
    
    local found=0
    
    # Search in .toml and .md files
    while IFS= read -r file; do
        while IFS= read -r line_num line_content; do
            if [[ "$line_content" =~ \{\{[A-Za-z_]+\}\} ]]; then
                log_error "Unresolved placeholder in $file:$line_num"
                found=$((found + 1))
            fi
        done < <(grep -n "{{" "$file" || true)
    done < <(find "$REPO_ROOT" -type f \( -name "*.toml" -o -name "*.md" \) 2>/dev/null || true)
    
    if [ $found -eq 0 ]; then
        log_ok "No unresolved placeholders"
    fi
}

validate_directories() {
    log_section "📁 ESTRUTURA DE DIRETÓRIOS"
    
    local dirs=("rules" "extensions" "scripts" "specs")
    
    for dir in "${dirs[@]}"; do
        if [ -d "$REPO_ROOT/$dir" ]; then
            log_ok "./$dir/ exists"
        else
            log_error "Missing required directory: ./$dir/"
        fi
    done
}

validate_permissions() {
    log_section "🔐 PERMISSÕES"
    
    local scripts=("scripts/v0.4.0/sync-constitution.py" "scripts/v0.4.0/validate-kit-install.sh")
    
    for script in "${scripts[@]}"; do
        script_path="$REPO_ROOT/$script"
        if [ -f "$script_path" ]; then
            if [ -x "$script_path" ]; then
                log_ok "$script is executable"
            else
                log_error "$script is not executable"
                echo "   Fix: chmod +x $script_path"
            fi
        fi
    done
}

validate_hooks() {
    log_section "🪝 HOOKS"
    
    log_ok "Hooks validation: TODO (placeholder)"
}

validate_toml_syntax() {
    log_section "📝 TOML SYNTAX"
    
    log_ok "TOML validation: TODO (placeholder - requires toml library)"
}

# === MAIN ===

main() {
    echo ""
    echo "🔍 VALIDAÇÃO DE INSTALAÇÃO DO KIT v0.4.0"
    echo "═════════════════════════════════════════"
    echo ""
    
    validate_placeholders
    validate_directories
    validate_permissions
    validate_hooks
    validate_toml_syntax
    
    echo ""
    echo "═════════════════════════════════════════"
    
    if [ $CRITICAL_ERRORS -gt 0 ]; then
        echo -e "${RED}CRITICAL ERRORS: $CRITICAL_ERRORS${NC}"
        return 2
    elif [ $ISSUES_FOUND -gt 0 ]; then
        echo -e "${YELLOW}ISSUES FOUND: $ISSUES_FOUND${NC}"
        return 1
    else
        echo -e "${GREEN}✅ VALIDATION PASSED${NC}"
        return 0
    fi
}

main
exit $?
