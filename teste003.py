import os
import cv2
from scripts.preprocessing import convert_to_gray, denoising, blur_image, ocr_plate, save_text_to_file, ocr_with_easyocr
import re


def extract_plate_from_text(text):
    # Remove any characters and numbers that come after the initial letters and special characters
    cleaned_text = re.sub(r'[^A-Z\-]+.*', '', text)
    
    # Convert to uppercase and remove any remaining special characters
    cleaned_text = re.sub(r'[^A-Z]+', '', cleaned_text).upper()
    
    return cleaned_text


def preprocess_image(input_folder, output_folder):
    # Certifique-se de que a pasta de saída existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Lista todos os arquivos na pasta de entrada
    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]

    for image_file in image_files:
        # Carrega a imagem
        img_path = os.path.join(input_folder, image_file)
        img = cv2.imread(img_path)

        # Aplica o pré-processamento
        gray_img = convert_to_gray(img)
        denoised_img = denoising(gray_img)
        blurred_img = blur_image(denoised_img)

        # Reconhece a placa com OCR e substitui caracteres inválidos
        plate_text = ocr_with_easyocr(blurred_img)  # Pass the processed image
        plate_text = [extract_plate_from_text(t) for t in plate_text]
        plate_text = ' '.join(plate_text)  # Join the list elements into a string

        # Salva o resultado em um arquivo de texto com o mesmo nome da imagem
        image_name_without_extension = os.path.splitext(image_file)[0]
        save_text_to_file(plate_text, output_folder, image_name_without_extension, "plate")



if __name__ == "__main__":
    input_folder = r"/media/vicrrs/Novo volume/CILIA/IMAGENS_PLACA/warped-with-errors-v1.1/antigo-v1"
    output_folder = r"/media/vicrrs/Novo volume/CILIA/TXT/PLACA_ANTIGA/EASYOCR"

    preprocess_image(input_folder, output_folder)
