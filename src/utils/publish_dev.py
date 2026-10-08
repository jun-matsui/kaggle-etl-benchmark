"""
Script utilitário para criar ou atualizar o rascunho do artigo diretamente na plataforma DEV.to via API oficial.
"""

import os
import sys
from pathlib import Path
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from src.config import DEV_COMMUNITY_API_KEY, DOCS_DIR

def publish_article_draft(publish_live: bool = False) -> dict:
    """
    Lê docs/dev_article_draft.md e envia para a API do DEV.to.
    Se publish_live=False, salva apenas como rascunho (draft) seguro.
    """
    draft_file = DOCS_DIR / "dev_article_draft.md"
    if not draft_file.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {draft_file}")
        
    with open(draft_file, "r", encoding="utf-8") as f:
        markdown_content = f.read()

    # Separa frontmatter simples se existir ou envia o corpo
    headers = {
        "api-key": DEV_COMMUNITY_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "article": {
            "title": "Benchmarking LLMs on ETL Logic Synthesis: Can AI Truly Replace Data Pipeline Scripting?",
            "published": publish_live,
            "body_markdown": markdown_content,
            "tags": ["kagglechallenge", "ai", "python", "machinelearning"]
        }
    }
    
    url = "https://dev.to/api/articles"
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code in [200, 201]:
        res_data = response.json()
        status_label = "PUBLICADO AO VIVO" if publish_live else "SALVO COMO RASCUNHO (DRAFT)"
        print(f"\n🎉 Artigo {status_label} com sucesso no DEV.to!")
        print(f"🔗 URL: {res_data.get('url')}")
        return res_data
    else:
        print(f"\n⚠️ Falha ao enviar para o DEV.to (Status {response.status_code}): {response.text}")
        return {"error": response.text, "status_code": response.status_code}

if __name__ == "__main__":
    publish_article_draft(publish_live=False)
