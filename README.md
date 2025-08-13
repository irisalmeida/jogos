# Pygame (pygame-ce) + pygbag → GitHub Pages

Estrutura:
```
assets/
  bruxo.png
  pedra_amarela.png
  pedra_azul.png
  pedra_verde.png
  pedra_vermelha.png
main.py
requirements.txt
.github/workflows/deploy.yml
```

## Como rodar local
```bash
python -m pip install -r requirements.txt
pygbag .
# abre http://localhost:8000 e gera build/web/
```

## Deploy no GitHub Pages (Actions)
- Faça push na branch `main`.
- Nas configurações do repositório: **Settings → Pages → Build and deployment → Source = GitHub Actions**.
- O workflow publica a pasta `build/web/` automaticamente.

## Observações
- Use `convert_alpha()` para PNGs com transparência (já implementado).
- O loop principal é assíncrono e chama `await asyncio.sleep(0)` a cada frame (necessário para WebAssembly).
