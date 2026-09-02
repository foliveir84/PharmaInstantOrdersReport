import streamlit as st
import pandas as pd
import os
import tempfile
from db_cleaner import get_cleaned_data, calculate_session_roi
from logic.ui_style import apply_custom_style, apply_corner_logo, init_session_state

# --- CONFIGURAÇÕES TÉCNICAS (ALTERAR MANUALMENTE SE NECESSÁRIO) ---
HUMAN_DISCOUNT_SECONDS = 20  # Segundos a descontar por verificação (Eficiência Humana)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="PharmaIntelligence | ROI Real",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INICIALIZAÇÃO ---
init_session_state()
apply_custom_style()
apply_corner_logo()

@st.cache_data(show_spinner="Analisando ciclos de trabalho...")
def load_and_clean_data(file_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    df = get_cleaned_data(tmp_path)
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)
    return df

# --- SIDEBAR ---
if os.path.exists("Logo.png"):
    st.sidebar.image("Logo.png", width='stretch')
else:
    st.sidebar.markdown("### 💊 PharmaInstantOrders")

st.sidebar.header("🛡️ Configurações ROI")
uploaded_file = st.sidebar.file_uploader("Upload Base de Dados (.db)", type="db")

st.sidebar.subheader("⚙️ Parâmetros Financeiros")
custo_hora = st.sidebar.number_input("Custo Hora Colaborador (€)", value=10.0, step=0.5, format="%.2f")

st.sidebar.subheader("⏱️ Ajuste de Sessão")
session_gap = st.sidebar.slider("Intervalo entre Sessões (min)", 15, 120, 60, help="Tempo para separar execuções do script.")

# --- PROCESSAMENTO ---
if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    df_raw = load_and_clean_data(file_bytes)
    
    if df_raw is not None and not df_raw.empty:
        # Filtro de Data
        min_date, max_date = df_raw['Date'].min(), df_raw['Date'].max()
        date_range = st.sidebar.date_input("Período:", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        
        if isinstance(date_range, tuple) and len(date_range) == 2:
            df_filtered = df_raw[(df_raw['Date'] >= date_range[0]) & (df_raw['Date'] <= date_range[1])].copy()
        else:
            df_filtered = df_raw.copy()

        # --- TÍTULO ---
        st.title("PharmaIntelligence - Análise de ROI Real")
        st.markdown(f"**Relatório de Disponibilidade** | {df_filtered['Date'].min().strftime('%d/%m/%Y')} a {df_filtered['Date'].max().strftime('%d/%m/%Y')}")
        
        # Cálculos de ROI
        num_sess, total_verif, horas_brutas, valor_total = calculate_session_roi(
            df_filtered, 
            custo_hora, 
            session_gap, 
            HUMAN_DISCOUNT_SECONDS
        )
        total_produtos = df_filtered['CNP'].nunique()

        # Formatação Portuguesa
        valor_formatado = f"{int(valor_total):,}".replace(",", ".") + "€"
        horas_arredondadas = f"{round(horas_brutas)} h"

        # KPIs Principais
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Produtos em Monitorização", f"{total_produtos:,}")
        k2.metric("Ciclos de Execução", f"{num_sess:,}")
        k3.metric("Tempo Retido", horas_arredondadas)
        k4.metric("Valor Poupado", valor_formatado)

        st.divider()

        # --- ANÁLISE POR PRODUTO ---
        st.subheader("🔍 Auditoria por Produto")
        all_products = sorted(df_filtered['PRODUTO_DISPLAY'].unique())
        selected_product = st.selectbox("Selecione o Produto para detalhe:", options=["Todos"] + all_products)
        
        if selected_product != "Todos":
            df_prod = df_filtered[df_filtered['PRODUTO_DISPLAY'] == selected_product]
            p_verif = df_prod.groupby(['TIME_STAMP', 'CNP']).size().shape[0]
            p_total_enq = df_prod['QT_ENCOMENDADA'].sum()
            
            p1, p2 = st.columns(2)
            p1.metric("Verificações de Stock", f"{p_verif}")
            p2.metric("Unidades Encomendadas", f"{int(p_total_enq)} un")
            matrix_data = df_prod
        else:
            matrix_data = df_filtered

        # --- MATRIZ DE FORNECEDORES ---
        st.subheader("📊 Matriz de Performance de Fornecedores")
        view_option = st.radio("Métrica da Matriz:", ["Unidades Encomendadas", "Unidades Disponíveis"], horizontal=True)
        metric_col = 'QT_ENCOMENDADA' if view_option == "Unidades Encomendadas" else 'QT_DISPONIVEL'
        
        df_suppliers_only = df_filtered[df_filtered['FORNECEDOR'] != '']
        top_suppliers = df_suppliers_only.groupby('FORNECEDOR')[metric_col].sum().sort_values(ascending=False).head(3).index.tolist()
        
        if top_suppliers:
            # Filtramos a matrix_data (que pode ser 1 produto ou todos) para os TOP 3
            df_matrix = matrix_data[(matrix_data['FORNECEDOR'] != '') & (matrix_data['FORNECEDOR'].isin(top_suppliers))]
            
            if not df_matrix.empty:
                pivot_matrix = df_matrix.pivot_table(index='PRODUTO_DISPLAY', columns='FORNECEDOR', values=metric_col, aggfunc='sum', fill_value=0)
                
                # Garantir que todas as colunas do Top 3 existem (corrige o KeyError)
                pivot_matrix = pivot_matrix.reindex(columns=top_suppliers, fill_value=0)

                if selected_product == "Todos":
                    pivot_matrix['TOTAL'] = pivot_matrix.sum(axis=1)
                    pivot_matrix = pivot_matrix.sort_values('TOTAL', ascending=False).head(20)
                
                st.dataframe(pivot_matrix, use_container_width=True)
            else:
                st.warning("Não existem transações registadas para os top fornecedores neste filtro.")
        else:
            st.warning("Sem dados de fornecedores ativos.")

        # --- GUIA DE INTERPRETAÇÃO ---
        st.divider()
        with st.expander("📖 Guia de Interpretação e Uso para Gestores"):
            st.markdown(f"""
            ### Como ler os resultados?
            Este dashboard traduz o trabalho do robô em **tempo de disponibilidade humana libertada**. 
            
            1. **Produtos em Monitorização:** Total de referências únicas vigiadas pelo sistema.
            2. **Ciclos de Execução:** Quantas vezes o script correu do início ao fim no período.
            3. **Tempo Retido:** Horas de trabalho que o robô executou por si. O cálculo já considera um desconto de **{HUMAN_DISCOUNT_SECONDS}s** por verificação para refletir a agilidade humana sobre a técnica do robô.
            4. **Valor Poupado:** Tradução das horas poupadas em Euros, baseada no custo/hora definido.
            
            ### Como ajustar os parâmetros?
            * **Custo Hora:** O valor do salário/hora do colaborador que executaria estas tarefas.
            * **Intervalo entre Sessões:** Define o tempo de paragem necessário para separar execuções distintas do robô.
            
            ### Análises Disponíveis:
            * **Auditoria por Produto:** Detalhe de verificações e compras de um medicamento específico.
            * **Matriz de Fornecedores:** Compara os 3 principais fornecedores por **Unidades Encomendadas** (entrega real) ou **Unidades Disponíveis** (melhor catálogo).
            """)

    else:
        st.error("Erro ao carregar os dados. Verifique o ficheiro.")
else:
    st.info("Aguardando upload da base de dados para calcular o ROI...")
