import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import zipfile
import PIL.ImageEnhance as ImageEnhance

def extract_selected_area(page_image, rect, scale_factor):
    x0 = int(rect["left"] / scale_factor)
    y0 = int(rect["top"] / scale_factor)
    width = int(rect["width"] / scale_factor)
    height = int(rect["height"] / scale_factor)    

    if isinstance(page_image, np.ndarray):
        page_image = Image.fromarray(page_image)    

    selected_area = page_image.crop((x0, y0, x0 + width, y0 + height))
    return selected_area

def create_zip_file(images):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for idx, img in enumerate(images):
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG', quality=100, optimize=False)
            zip_file.writestr(f"imagem_{idx+1}.png", img_buffer.getvalue())
    
    zip_buffer.seek(0)
    return zip_buffer

def process_transparent_background(image):
    opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)    
    gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)    
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)    
    b, g, r = cv2.split(opencv_image)
    alpha = thresh
    transparent_image = cv2.merge([b, g, r, alpha])
    transparent_pil = Image.fromarray(cv2.cvtColor(transparent_image, cv2.COLOR_BGRA2RGBA))
    return transparent_pil

def create_transparent_zip(images, adjustments):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for idx, img in enumerate(images):
            adjusted_img = img
            if isinstance(adjusted_img, np.ndarray):
                adjusted_img = Image.fromarray(adjusted_img)
            
            enhancer = ImageEnhance.Brightness(adjusted_img)
            adjusted_img = enhancer.enhance(adjustments[idx]['brightness'])            
    
            transparent_img = process_transparent_background(adjusted_img)            

            img_buffer = io.BytesIO()
            transparent_img.save(img_buffer, format='PNG', quality=100, optimize=False)
            
            image_name = st.session_state.image_names.get(idx, f"imagem_{idx+1}")
            if not image_name.lower().endswith('.png'):
                image_name = f"{image_name}_transparente.png"
            
            zip_file.writestr(image_name, img_buffer.getvalue())
    
    zip_buffer.seek(0)
    return zip_buffer 