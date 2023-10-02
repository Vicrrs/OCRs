import cv2
import easyocr
import pytesseract
import os
import re
from scripts.preprocessing import *

# Pasta de entrada com as imagens
input_folder = r"/home/tkroza/Downloads/warped-with-errors-v1.1/antigo-v1"
# Pasta para salvar os resultados do pytesseract
pytesseract_output_folder = r"/home/tkroza/LAMIA/CILIA/code/OCRs/teste/antiga/tesseract"
# Pasta para salvar os resultados do easyocr
easyocr_output_folder = r"/home/tkroza/LAMIA/CILIA/code/OCRs/teste/antiga/easy"

# Lista de idiomas desejados para o easyocr
easyocr_lang_list = ['pt']

# Caracteres permitidos (letras e números)
allowed_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

# Garanta que as pastas de saída existam
os.makedirs(pytesseract_output_folder, exist_ok=True)
os.makedirs(easyocr_output_folder, exist_ok=True)

# Lista de extensões de arquivo de imagem suportadas
image_extensions = [".png"]

def process_image(image_path):
    # Carrega a imagem
    img = cv2.imread(image_path)
    img_gray = convert_to_gray(img)
    img_den = denoising(img_gray)
    img_blur = blur_image(img_den)

    # Realiza OCR com pytesseract e easyocr
    text_py = ocr_plate(img_blur)  # Você pode escolher entre img_gray e img_blur
    
    # Use pytesseract para filtrar apenas os caracteres permitidos
    text_py = re.sub(f"[^{allowed_characters}]", "", text_py)

    text_easy = ocr_with_easyocr(img_blur)  # Você pode escolher entre img_gray e img_blur

    # Filtrar apenas os caracteres permitidos no texto do easyocr
    text_easy = [re.sub(f"[^{allowed_characters}]", "", t) for t in text_easy]

    # Realize o pós-processamento para garantir a ordem "LETRA LETRA LETRA NUMERO LETRA NUMERO NUMERO"
    text_py = postprocess_text(text_py)
    text_easy = [postprocess_text(t) for t in text_easy]

    # Extraia o nome do arquivo sem a extensão
    image_name = os.path.basename(image_path)
    image_name_without_extension = os.path.splitext(image_name)[0]

    # Salvar os resultados do pytesseract
    pytesseract_output_file = os.path.join(pytesseract_output_folder, f"{image_name_without_extension}.txt")
    with open(pytesseract_output_file, "w", encoding="utf-8") as file:
        file.write(text_py)

    # Salvar os resultados do easyocr
    easyocr_output_file = os.path.join(easyocr_output_folder, f"{image_name_without_extension}.txt")
    with open(easyocr_output_file, "w", encoding="utf-8") as file:
        file.write("\n".join(text_easy))

def postprocess_text(text):
    # Remova caracteres não alfanuméricos e converta para maiúsculas
    text = re.sub(r'[^A-Za-z0-9]', '', text).upper()

    # Se o texto for mais curto que 7 caracteres, retorne vazio
    if len(text) < 7:
        return ""

    # Reorganize o texto para a ordem "LETRA LETRA LETRA NUMERO LETRA NUMERO NUMERO"
    processed_text = (
        text[0] + text[1] + text[2] +  # Três primeiras letras
        text[3] +  # Primeiro número
        text[4] +  # Quarta letra
        text[5] +  # Segundo número
        text[6]    # Terceiro número
    )

    return processed_text

if __name__ == "__main__":
    # Percorre os arquivos na pasta de entrada
    for filename in os.listdir(input_folder):
        if any(filename.lower().endswith(ext) for ext in image_extensions):
            image_path = os.path.join(input_folder, filename)
            process_image(image_path)
