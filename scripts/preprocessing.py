import cv2
import easyocr
import pytesseract
from matplotlib import pyplot as plt
import os


def convert_to_gray(img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray_img


def denoising(img):
    denoised_img = cv2.fastNlMeansDenoising(img, None, 10, 7, 21)
    return denoised_img


def blur_image(gray_img):
    blur_img = cv2.bilateralFilter(gray_img, 11, 17, 17)
    return blur_img


def thresholding(image):
    thrs = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    return thrs


def save_text_to_file(text, output_folder, image_name_without_extension, suffix):
    file_name = f"{image_name_without_extension}_{suffix}.txt"
    file_path = os.path.join(output_folder, file_name)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(text)


def ocr_with_easyocr(img):
    # Lista de idiomas desejados, por exemplo, 'en' para inglês
    lang_list = ['pt']

    # Inicializa o leitor com a lista de idiomas
    reader = easyocr.Reader(lang_list)

    results = reader.readtext(img)
    extracted_text = [result[1] for result in results]
    return extracted_text


def ocr_plate(plate):
    config_tesseract = "--psm 10 --oem 3 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    text = pytesseract.image_to_string(
        plate, lang="por", config=config_tesseract)
    text = "".join(c for c in text if c.isalnum())
    return text


def extract_text(results):
    text_list = []
    for result in results:
        if isinstance(result, tuple) and len(result) >= 2:
            text_list.append(result[1])
    return ' '.join(text_list)


def show_img(img):
    plt.imshow(img, cmap="gray")
    plt.show()
