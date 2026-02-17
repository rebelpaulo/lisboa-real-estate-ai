#!/bin/bash
# Script de automação do Lisboa Real Estate AI
# Corre o scraper e atualiza o dashboard

cd /root/.openclaw/workspace/lisboa-real-estate-ai/agent
source venv/bin/activate

echo "=========================================="
echo "🚀 LISBOA REAL ESTATE AI - AUTOMAÇÃO"
echo "=========================================="
echo "Data: $(date)"
echo ""

# 1. Correr scraper de leilões
echo "📊 1. A extrair dados de leilões..."
python scraper_rapido.py > logs/scraper_$(date +%Y%m%d_%H%M%S).log 2>&1

# 2. Analisar oportunidades
echo "🧠 2. A analisar oportunidades..."
python demo_sistema.py > logs/analise_$(date +%Y%m%d_%H%M%S).log 2>&1

# 3. Guardar resultados
echo "💾 3. A guardar resultados..."
cp oportunidades_demo.json ../dashboard/public/data/oportunidades.json

# 4. Commit para GitHub (ativa o deploy Vercel)
echo "📤 4. A sincronizar com GitHub..."
cd /root/.openclaw/workspace/lisboa-real-estate-ai
git add agent/oportunidades_demo.json dashboard/public/data/
git commit -m "Auto-update: $(date +%Y-%m-%d_%H:%M)"
git push origin main

echo ""
echo "✅ Automação completa!"
echo "Dashboard atualizado: https://lisboa-real-estate-jeeehva5h-originaly-gmailcoms-projects.vercel.app"
echo "=========================================="
