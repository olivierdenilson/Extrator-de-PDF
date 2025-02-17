import streamlit as st
from src.app import main as app_main

# Configuração da página com ícone personalizado
st.set_page_config(
    page_title="Extrator de Imagens PDF",
    page_icon="📄",  # Usando o mesmo ícone do título
    layout="wide"
)

# Estilização dos botões
st.markdown("""
    <style>
    .stButton button[kind="secondary"] {
        background-color: #FFD700;
        color: black;
        border: 2px solid #FFD700;
    }
    .stButton button[kind="secondary"]:hover {
        border-color: #FFD700;
        background-color: #FFE44D;
    }
    .stButton button[kind="primary"] {
        background-color: #FF6B6B;
        color: white;
        border: 2px solid #FF6B6B;
    }
    .stButton button[kind="primary"]:hover {
        border-color: #FF6B6B;
        background-color: #FF8585;
    }
    </style>
""", unsafe_allow_html=True)

# Configuração do menu lateral
def sidebar_menu():
    st.sidebar.title("Menu")
    menu_option = st.sidebar.radio(
        "Selecione uma opção:",
        ["Extrator de Imagens", "Sobre"],
        key="menu_radio"
    )
    return menu_option

def show_help():
    st.title("Sobre o Aplicativo")
    st.markdown("""
    ### Extrator de Imagens PDF
    #     
    Este aplicativo foi desenvolvido para facilitar a extração e o processamento de imagens de arquivos PDF.
    
    #### Funcionalidades:
    - Extração de imagens de arquivos PDF
    - Ajuste de brilho das imagens
    - Remoção de fundo das imagens
    - Download das imagens processadas
                
    """)

def main():
    menu_option = sidebar_menu()
    
    if menu_option == "Extrator de Imagens":
        app_main()
    else:
        show_help()

if __name__ == "__main__":
    main() 