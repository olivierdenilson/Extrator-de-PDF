import streamlit as st
from streamlit_drawable_canvas import st_canvas
import fitz
from PIL import Image
import io
from pdf2image import convert_from_bytes
import numpy as np
import os
from .utils import (
    extract_selected_area,
    create_zip_file,
    process_transparent_background,
    create_transparent_zip
)
import requests

def main():
    if "extracted_images" not in st.session_state:
        st.session_state.extracted_images = []
    if "image_names" not in st.session_state:
        st.session_state.image_names = {}
    if "image_adjustments" not in st.session_state:
        st.session_state.image_adjustments = {}

    # Carregando e exibindo a logo da URL
    logo_url = "http://cadastrousuario.gruposanta.com.br//images/logo_topo.png"
    
    # Usando uma coluna menor para a logo
    col1, col2 = st.columns([1, 4])
    with col1:
        try:
            # Adicionando CSS para ajustar o tamanho e alinhamento
            st.markdown(
                """
                <style>
                [data-testid="stImage"] {
                    width: 200px !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            st.image(logo_url)
        except:
            st.error("Não foi possível carregar a logo")
    
    st.title("📄 Extrator de Imagens PDF")
    
    # CSS para traduzir o texto do upload
    st.markdown("""
        <style>
        .uploadedFile {
            display: none;
        }
        .stFileUploader > div > div::before {
            content: "Arraste e solte o arquivo aqui";
        }
        </style>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Arraste e solte o arquivo PDF aqui",
        type="pdf",
        help="Selecione ou arraste um arquivo PDF"
    )
    
    # Verifica se o arquivo foi removido
    if "previous_file" not in st.session_state:
        st.session_state.previous_file = None
    
    # Se o arquivo atual é None e o anterior não era, significa que o arquivo foi removido
    if uploaded_file is None and st.session_state.previous_file is not None:
        st.session_state.extracted_images = []
        st.session_state.image_names = {}
        st.session_state.image_adjustments = {}
        st.session_state.last_selection = None
        st.session_state.previous_file = None
        st.rerun()
    
    # Atualiza o arquivo anterior
    if uploaded_file is not None:
        st.session_state.previous_file = uploaded_file
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        page_number = st.number_input("Selecione a página", min_value=1, max_value=len(doc), value=1) - 1
        
        page = doc[page_number]
        pix = page.get_pixmap()
        img_data = pix.tobytes("png")
        
        images = convert_from_bytes(pdf_bytes)
        page_image = images[page_number]
        
        width = page_image.width
        height = page_image.height
        
        # Calculando as dimensões ajustadas
        max_width = 800  # Largura máxima desejada
        scale_factor = max_width / width
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=2,
            stroke_color="#FFD700",
            background_image=Image.open(io.BytesIO(img_data)),
            height=new_height,
            width=new_width,
            drawing_mode="rect",
            key=f"canvas_{page_number}",
        )
        
        if canvas_result.json_data is not None and len(canvas_result.json_data["objects"]) > 0:
            selected_rect = canvas_result.json_data["objects"][-1]
            
            # Verifica se é uma nova seleção comparando com a última seleção
            if "last_selection" not in st.session_state:
                st.session_state.last_selection = None
            
            current_selection = str(selected_rect)  # Converte para string para comparação
            
            if current_selection != st.session_state.last_selection:
                selected_area = extract_selected_area(page_image, selected_rect, scale_factor)
                st.session_state.extracted_images.append(selected_area)
                st.session_state.image_adjustments[len(st.session_state.extracted_images)-1] = {'brightness': 1.0}
                st.session_state.last_selection = current_selection
                st.rerun()
            
            col1, col2 = st.columns([2,1])
            with col2:
                if st.button("Limpar todas as seleções", type="secondary", use_container_width=True):
                    st.session_state.extracted_images = []
                    st.session_state.image_names = {}
                    st.session_state.image_adjustments = {}
                    st.session_state.last_selection = None
                    st.rerun()
        
        if st.session_state.extracted_images:
            total_images = len(st.session_state.extracted_images)
            st.write(f"Imagens Extraídas: ({total_images} {'imagem' if total_images == 1 else 'imagens'})")
            
            for idx, img in enumerate(st.session_state.extracted_images):
                col1, col2, col3, col4 = st.columns([1.5,1.5,1.5,1])
                
                with col1:
                    image_name = st.text_input(
                        "Nome da imagem",
                        value=st.session_state.image_names.get(idx, f"imagem_{idx+1}"),
                        key=f"name_{idx}",
                        label_visibility="collapsed"
                    )
                    st.session_state.image_names[idx] = image_name
                
                with col2:
                    brightness = st.slider(
                        "Brilho",
                        0.0, 2.0, 
                        st.session_state.image_adjustments[idx]['brightness'],
                        key=f"bright_{idx}"
                    )
                    st.session_state.image_adjustments[idx]['brightness'] = brightness
                
                with col3:
                    st.image(img, caption=f"Imagem {idx+1}", use_container_width=True)
                
                with col4:
                    if st.button("🗑️ Excluir", key=f"del_btn_{idx}", type="primary"):
                        st.session_state.extracted_images.pop(idx)
                        st.session_state.image_names.pop(idx, None)
                        st.session_state.image_adjustments.pop(idx, None)
                        st.rerun()
            
            if st.session_state.extracted_images:
                zip_buffer = create_zip_file(st.session_state.extracted_images)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="Baixar Imagens Originais",
                        data=zip_buffer,
                        file_name="imagens_extraidas.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
                
                with col2:
                    transparent_zip = create_transparent_zip(
                        st.session_state.extracted_images,
                        st.session_state.image_adjustments
                    )
                    st.download_button(
                        label="Baixar com Fundo Transparente",
                        data=transparent_zip,
                        file_name="imagens_transparentes.zip",
                        mime="application/zip",
                        use_container_width=True
                    ) 