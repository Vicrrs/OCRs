import easyocr

# Inicializa o leitor do EasyOCR com o idioma desejado
reader = easyocr.Reader(['en'])  # Use 'en' para inglês

# Carrega a imagem que você deseja ler
image_path = 'caminho_para_sua_imagem.jpg'
results = reader.readtext(image_path)

# Exibe os resultados
for (bbox, text, prob) in results:
    print(f'Texto: {text}, Probabilidade: {prob}')

# Fecha o leitor
reader.close()