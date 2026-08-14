#!/usr/bin/env bash
# bootstrap.sh | Vitalia Kit 0.3
# Instalação global do kit em ~/.vitalia/kit/
#
# Uso remoto:
#   sh -c "$(curl -fsSL https://raw.githubusercontent.com/vitalia-platform/spec-agents/main/bootstrap.sh)"
#
# Uso local (desenvolvimento):
#   bash ~/.vitalia/kit/scripts/bootstrap.sh

set -e

VITALIA_HOME="${HOME}/.vitalia"
KIT_DIR="${VITALIA_HOME}/kit"
KIT_REPO="git@github.com:vitalia-platform/spec-agents.git"
REQUIRED_VERSION="0.3.0"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║    Vitalia Kit 0.3 — Instalador Global   ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ─── Verificar ~/.vitalia/ ────────────────────────────────────
if [ ! -d "${VITALIA_HOME}" ]; then
    echo "📁 Criando ~/.vitalia/ pela primeira vez..."
    mkdir -p "${VITALIA_HOME}"/{config,cache,apps}
    echo "   ✅ Estrutura base criada."
else
    echo "📁 ~/.vitalia/ já existe."
fi

# ─── Verificar ~/.vitalia/kit/ ────────────────────────────────
if [ -d "${KIT_DIR}/.git" ]; then
    INSTALLED_VERSION=$(cat "${KIT_DIR}/VERSION" 2>/dev/null || echo "unknown")
    echo "📦 Kit detectado: versão ${INSTALLED_VERSION}"

    if [ "${INSTALLED_VERSION}" = "${REQUIRED_VERSION}" ]; then
        echo "   ✅ Versão atual. Verificando atualizações..."
        git -C "${KIT_DIR}" pull --ff-only origin main 2>/dev/null && \
            echo "   ✅ Atualizado." || \
            echo "   ⚠️  Pull falhou (sem rede?). Usando versão local."
    else
        echo "   🔄 Upgrade ${INSTALLED_VERSION} → ${REQUIRED_VERSION}..."
        git -C "${KIT_DIR}" fetch origin
        git -C "${KIT_DIR}" checkout main
        git -C "${KIT_DIR}" pull --ff-only origin main
        echo "   ✅ Upgrade concluído: $(cat "${KIT_DIR}/VERSION")"
    fi
else
    echo "⬇️  Clonando spec-agents em ${KIT_DIR}..."
    git clone --depth=1 "${KIT_REPO}" "${KIT_DIR}"
    echo "   ✅ Kit instalado: v$(cat "${KIT_DIR}/VERSION")"
fi

echo ""
echo "✅ Vitalia Kit $(cat "${KIT_DIR}/VERSION") instalado em ${KIT_DIR}"
echo ""
echo "Para ativar num projeto específico:"
echo "  cd /seu/projeto && bash ~/.vitalia/kit/scripts/install-project.sh"
echo ""
