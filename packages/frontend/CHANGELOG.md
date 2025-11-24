# Histórico de Mudanças - Frontend

## [0.1.1] - 2025-11-24

### 🐛 Correções

- **Correção do Botão de Login:** Resolvido um problema onde o botão de login não funcionava devido a uma configuração incorreta da opção `skip` no hook `useApi`. A função `execute` do hook agora é chamada corretamente, permitindo que a requisição de login seja enviada ao backend.

### 🧪 Testes

- **Configuração Inicial do Jest:** Adicionada a configuração inicial para o Jest, incluindo `babel.config.js`, `jest.config.js` e `jest.setup.js`, para habilitar testes unitários para os componentes e hooks do frontend.
- **Teste para o Hook `useApi`:** Criado o arquivo `use-api.test.ts` com testes para validar o comportamento do hook `useApi`, garantindo que ele gerencie corretamente os estados de carregamento, dados e erros, bem como a execução condicional da API.

## [0.1.0] - 2025-11-24

### 🎯 Novas Funcionalidades

- **Implementação da Página de Login:** Desenvolvimento inicial da página de login com formulário de autenticação.
- **Integração com API de Autenticação:** Conectado o formulário de login com o endpoint de autenticação do backend usando o hook `useApi`.
