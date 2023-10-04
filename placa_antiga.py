import cv2
import easyocr
import pytesseract
import os
import re
from scripts.preprocessing import *


# Pasta de entrada com as imagens
input_folder = r"/media/vicrrs/Novo volume/CILIA/IMAGENS_PLACA/warped-with-errors-v1.1/antigo-v1"
# Pasta para salvar os resultados do pytesseract
pytesseract_output_folder = r"/media/vicrrs/Novo volume/CILIA/TXT/PLACA_ANTIGA/PYTESSERACT"
# Pasta para salvar os resultados do easyocr
easyocr_output_folder = r"/media/vicrrs/Novo volume/CILIA/TXT/PLACA_ANTIGA/EASYOCR"

# Lista de idiomas desejados para o easyocr
easyocr_lang_list = ['pt']

# Caracteres permitidos (letras e números)
allowed_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

mapeamento = {
    '1': 'I',
    '0': 'O',
    '2': 'Z',
    '3': 'E',
    '4': 'A',
    '5': 'S',
    '6': 'G',
    '7': 'T',
    '8': 'B',
    '9': 'P'
}


def extract_plate_from_text(text):
    cleaned_text = re.sub(r'[-;:.]', '', text)
    
    return cleaned_text[:3].upper()

def substituir_caracteres(caractere):
    if caractere.isdigit():
        return mapeamento.get(caractere, caractere)
    elif caractere.isalpha():
        return mapeamento.get(caractere.upper(), caractere)
    return caractere

def converter_placa(placa):
    placa_convertida = ''.join([substituir_caracteres(caractere).upper() for caractere in placa])
    return placa_convertida

os.makedirs(pytesseract_output_folder, exist_ok=True)
os.makedirs(easyocr_output_folder, exist_ok=True)

image_extensions = [".png"]

def process_image(image_path):
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

    # Realize o pós-processamento para garantir 3 letras e 4 números
    text_py = postprocess_text(text_py)
    text_easy = [postprocess_text(t) for t in text_easy]

    # Converter o texto em maiúsculas antes de salvar
    text_py = text_py.upper()
    text_easy = [t.upper() for t in text_easy]

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
    # Remova qualquer caractere que não seja uma letra ou um número
    filtered_text = ''.join(char for char in text if char.isalnum())

    # Se o texto não tiver pelo menos 7 caracteres, mantenha-o inalterado
    if len(filtered_text) < 7:
        return text

    # Pegue os três primeiros caracteres (letras) e os quatro últimos (números)
    letters = filtered_text[:3].upper()
    numbers = filtered_text[-4:]

    # Monte a placa no formato desejado
    formatted_placa = f"{letters}{numbers}"

    return formatted_placa


if __name__ == "__main__":
    # Percorre os arquivos na pasta de entrada
    for filename in os.listdir(input_folder):
        if any(filename.lower().endswith(ext) for ext in image_extensions):
            image_path = os.path.join(input_folder, filename)
            process_image(image_path)