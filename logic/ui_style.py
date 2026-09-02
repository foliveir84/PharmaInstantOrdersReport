import streamlit as st
import base64
import os

def init_session_state():
    """Inicializa variáveis globais que devem persistir entre páginas."""
    defaults = {
        "custo_hora": 12.0,
    }
    
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def apply_custom_style():
    """Aplica o design System 'PharmaTouch Glass'."""
    st.markdown("""
    <style>
        /* Fundo e Estrutura Geral */
        .stApp {
            background: linear-gradient(135deg, #0e0b16 0%, #1a1625 100%);
        }
        
        /* Headers com Gradiente Suave */
        h1, h2, h3 {
            background: -webkit-linear-gradient(0deg, #00e5ff, #d900ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700 !important;
            letter-spacing: -0.5px;
        }
        
        /* Glassmorphism Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        
        /* Inputs Modernos */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #f0f2f6 !important; /* Texto visível (cor de texto do tema) */
            border-radius: 8px !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #d900ff !important;
            box-shadow: 0 0 0 1px #d900ff !important;
        }
        
        /* Placeholder Visível - Mais específico */
        .stTextInput input::placeholder, .stTextArea textarea::placeholder {
            color: rgba(255, 255, 255, 0.4) !important; /* Cinzento claro para contraste */
            opacity: 1 !important;
        }
        
        /* Botões */
        .stButton button {
            border-radius: 8px;
            font-weight: 600;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            background: linear-gradient(90deg, #d900ff, #00e5ff);
            color: white;
            border: none;
        }

        /* Sidebar Background */
        [data-testid="stSidebar"] {
            background-color: #1A1625; /* Usa a cor secundária do tema */
        }
        
        /* Custom Metrics Style matching the theme */
        .metric-container {
            background: rgba(255,255,255,0.05); 
            padding: 15px; 
            border-radius: 10px; 
            border-left: 5px solid #00e5ff;
            color: #fff;
        }
    </style>
    """, unsafe_allow_html=True)

def apply_corner_logo(path="assets/logo_corner.png", height=36):
    """Logotipo persistente no canto superior direito (badge branco legivel no tema escuro)."""
    if not os.path.exists(path):
        return
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
            .brand-corner {{
                position: fixed;
                top: 12px;
                right: 16px;
                z-index: 999999;
                background: rgba(255, 255, 255, 0.96);
                padding: 8px 14px;
                border-radius: 12px;
                box-shadow: 0 4px 18px rgba(0, 0, 0, 0.35);
                display: flex;
                align-items: center;
            }}
            .brand-corner img {{
                height: {height}px;
                width: auto;
                display: block;
            }}
            @media (max-width: 768px) {{
                .brand-corner img {{ height: 28px; }}
                .brand-corner {{ padding: 6px 10px; }}
            }}
        </style>
        <div class="brand-corner">
            <img src="data:image/png;base64,{b64}" alt="Rede Premium Farma">
        </div>
        """,
        unsafe_allow_html=True,
    )