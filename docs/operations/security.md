# Melhores Práticas de Segurança

Este documento descreve as medidas de segurança implementadas no Investment Backend para proteger informações sensíveis e garantir uma operação segura.

## Segurança de Chaves de API

- **Sem chaves de API no código** - Todas as chaves de API são carregadas a partir de variáveis de ambiente.
- **Variáveis de ambiente** - Configurações sensíveis são armazenadas em arquivos `.env` (não commitados no controle de versão).
- **Validação de entrada** - Todas as entradas externas são validadas para prevenir ataques de injeção.
- **Limitação de taxa (Rate limiting)** - Implementado para prevenir abuso de APIs externas.

## Desenvolvimento Seguro

### Hooks de Pre-commit

Um hook de pre-commit está incluído para prevenir commits acidentais de informações sensíveis. Ele verifica por:
- Chaves de API e segredos
- Senhas no código
- Tokens e credenciais

Para instalar o hook de pre-commit:

```bash
chmod +x .githooks/pre-commit
cp .githooks/pre-commit .git/hooks/
```

### Verificações de Segurança

Um script de verificação de segurança está disponível em `scripts/security_check.py` que pode ser executado manualmente ou em pipelines de CI/CD para detectar:
- Segredos no código
- Dependências vulneráveis
- Más configurações

## Configuração de Ambiente

1.  Copie `.env.example` para `.env`:
    ```bash
    cp .env.example .env
    ```

2.  Atualize o arquivo `.env` com suas chaves de API e configurações:
    ```env
    # Chaves de API obrigatórias
    FINNHUB_API_KEY=sua_chave_de_api_do_finnhub_aqui
    ALPHA_VANTAGE_API_KEY=sua_chave_de_api_do_alpha_vantage_aqui

    # Configuração opcional
    ENABLE_CACHE=true
    CACHE_TTL_SECONDS=3600
    ```

3.  Nunca commite o arquivo `.env` no controle de versão.

## Dependências

Atualize regularmente as dependências para incluir patches de segurança. Use:

```bash
pip list --outdated
pip install -U nome_do_pacote
```

## Reportando Problemas de Segurança

Se você descobrir uma vulnerabilidade de segurança, por favor, reporte aos mantenedores do projeto. Não crie uma issue pública.
