# PharmaIntelligence | Dashboard de ROI Real e Performance (v3.1)

## 1. Visão Geral do Projeto
Este dashboard foi desenhado para provar o valor operacional e financeiro da automação de encomendas em farmácias. A versão atual (v3.1) foca-se na **disponibilidade libertada**, medindo o tempo real que o robô substitui o trabalho humano.

**Destaque v3.1:** Transição de uma métrica baseada em "tempo por tarefa" para uma métrica baseada em **"Janela de Execução"**, capturando a duração total dos ciclos de trabalho.

## 2. Estrutura Técnica (Arquitetura Modular)
*   **`db_cleaner.py` (Cérebro ETL & ROI):**
    *   **Monitorização Total:** Mantém registos com e sem fornecedor para identificar o início e fim real de cada ciclo do script.
    *   **Normalização CNP:** Unifica descrições para garantir que cada produto é contabilizado uma única vez.
    *   **Lógica de Sessões:** Agrupa registos por proximidade temporal (gaps > 60min criam nova sessão).
*   **`app_dashboardv3.py` (Interface Avançada):**
    *   **Cache Inteligente:** Utiliza `@st.cache_data` para processamento instantâneo.
    *   **Sliders de Ajuste:** Permite configurar o "Custo Hora" e o "Desconto de Eficiência Humana" em tempo real.

## 3. Lógica de ROI Real (v3.1)

### ⏱️ Cálculo por Janela de Sessão
Ao contrário de modelos teóricos, o sistema agora mede o tempo real:
1.  **Deteção de Ciclos:** Identifica quando o robô começou e terminou uma execução completa.
2.  **Duração Bruta:** `Tempo_Final - Tempo_Inicial` de cada sessão.
3.  **Fator de Correção Humana:** Subtrai um overhead técnico (ex: 20s) por cada produto verificado. Isto remove o tempo de espera do HTML/Script que um humano não teria, tornando o ROI extremamente realista.
4.  **Valor em Euros:** `Tempo_Ajustado_Total * Custo_Hora_Colaborador`.

## 4. Funcionalidades de Auditoria
*   **Produtos em Monitorização:** Contagem real de todos os CNPs únicos vigiados pelo sistema (independente de haver encomenda).
*   **Matriz de Fornecedores Dinâmica:** Compara os **Top 3 Fornecedores** (calculados dinamicamente) em duas vertentes:
    *   **Unidades Encomendadas:** Quem está realmente a abastecer a farmácia.
    *   **Unidades Disponíveis:** Quem costuma ter o stock em catálogo (auditoria de catálogo).
*   **Filtro por Produto:** Detalhe exato de quantas vezes um item foi verificado e quantas unidades foram compradas no período.

## 5. Como Executar
1. Instalar dependências: `pip install -r requirements.txt`
2. Executar v3.1: `streamlit run app_dashboardv3.py`
3. Carregar o ficheiro `bd_order_history.db` na barra lateral.

## 6. Histórico de Versões
*   **v3.1 (Atual):** Monitorização total (registos vazios incluídos para ROI), Deteção de Sessões e Fator de Correção Humana.
*   **v3.0:** Introdução da matriz dinâmica de fornecedores e lógica inicial de sessões.
*   **v2.x:** Lógica de "Valor Retido" baseada apenas em segundos por linha (obsoleta pelo viés de simultaneidade).
