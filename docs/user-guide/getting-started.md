# Guia do Usuário: Primeiros Passos

Bem-vindo à Plataforma de Análise de Investimentos! Este guia ajudará você a entender as funcionalidades da plataforma e como utilizá-las para tomar decisões informadas sobre seus investimentos.

## Visão Geral do Produto

Esta plataforma foi projetada para oferecer uma análise profunda e profissional de portfólios de investimento, combinando métricas financeiras avançadas com visualizações intuitivas.

### Funcionalidades Principais

#### 1. Envio de Operações (v0.7.0)
A página de envio de operações permite cadastrar suas compras e vendas de ativos de forma simples e intuitiva.

-   **Formatação de Moeda**: Valores são exibidos no formato brasileiro (R$ 100.000,00)
-   **Digitação Fluida**: Ao clicar no campo, você digita normalmente; ao sair, o valor é formatado
-   **Validação em Tempo Real**: Erros são exibidos por operação com mensagens claras
-   **Tipos de Operação**: Escolha entre "Compra" e "Venda"
-   **Persistência Local**: Seus dados são salvos automaticamente no navegador

#### 2. Análise de Desempenho e Risco
Esta é a base para qualquer análise de investimento, permitindo uma avaliação completa da performance histórica de um portfólio.

-   **Métricas de Desempenho:** 
    - **Retorno Acumulado:** Visualize o crescimento total do seu investimento ao longo do tempo.
    - **Volatilidade Anualizada:** Entenda o grau de oscilação dos seus ativos e o risco associado.

-   **Índices Ajustados ao Risco:**
    - **Índice de Sharpe:** Mede o retorno obtido para cada unidade de risco assumida. Quanto maior, melhor.
    - **Índice de Sortino:** Similar ao Sharpe, mas foca apenas na volatilidade negativa (o "risco ruim"), oferecendo uma perspectiva sobre a eficiência do portfólio em evitar perdas.

-   **Análise de Risco de Cauda (Tail Risk):**
    - **Value at Risk (VaR):** Estima a perda máxima esperada para um determinado nível de confiança (ex: "há 95% de chance de que as perdas não excedam X em um dia").
    - **Conditional Value at Risk (CVaR):** Calcula a média das perdas que ocorrem *além* do VaR, dando uma imagem mais clara do prejuízo potencial durante os piores cenários de mercado.

#### 3. Otimização de Portfólio com Fronteira Eficiente
Baseada no trabalho do prêmio Nobel Harry Markowitz, esta ferramenta ajuda a construir a carteira "perfeita".

-   **Conceito:** A ferramenta calcula e desenha uma curva em um gráfico de risco vs. retorno. Cada ponto nesta curva representa um portfólio "ótimo" (maior retorno possível para um nível de risco).
-   **Tomada de Decisão:** Identifique o **Portfólio de Variância Mínima** (menor risco) ou o **Portfólio de Máximo Sharpe** (melhor relação risco/retorno) para ajustar sua carteira ao seu perfil.

#### 4. Visualizações Avançadas e Interativas
Entenda a dinâmica interna do seu portfólio através de gráficos interativos.

-   **Matriz de Correlação:** Mostra como cada ativo se move em relação aos outros. Essencial para diversificação.
-   **Contribuição de Risco por Ativo:** Mostra qual porcentagem do risco total vem de cada ativo.
-   **Rolling Returns (Retornos Móveis):** Mostra a consistência da performance em diferentes janelas de tempo.
-   **Drawdown:** Destaca a magnitude e a duração das piores quedas que o portfólio sofreu.

#### 5. Simulação de Monte Carlo
Olhe para o futuro e responda: "Qual é a gama de resultados possíveis para o meu portfólio?"

-   **Processo:** Executa milhares de simulações de preços futuros baseadas em dados históricos.
-   **Resultado:** Uma distribuição de probabilidade de resultados possíveis, ajudando a visualizar a chance de atingir suas metas financeiras.

#### 6. Segurança
-   **Autenticação Segura:** Seus dados são protegidos por um sistema de autenticação robusto utilizando JSON Web Tokens (JWT).

---

## Próximos Passos

- Explore os [Tutoriais](tutorials/) para aprender a usar cada ferramenta passo-a-passo.
- Consulte a seção de [Funcionalidades](features/) para detalhes técnicos sobre cada métrica.
