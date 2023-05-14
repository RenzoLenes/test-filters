from flask import Flask, request, render_template
from PIL import Image, ImageFilter
import numpy as np

app = Flask(__name__)
original_image = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=['POST'])
def upload():
    global original_image
    file = request.files['file']
    filter = request.form.get('filter')

    if file:
        try:
            original_image = Image.open(file)
            original_image.save('static/uploads/original_image.png', format='PNG')
        except Exception as e:
            error_message = f"Error: {str(e)}"
            return render_template("index.html", error_message=error_message)

    if original_image is None:
        return render_template("index.html", error_message="Please upload an image first.")

    filtered_image = apply_filter(original_image, filter)
    if filtered_image is None:
        return render_template("index.html", error_message="Invalid filter selected.")

    filtered_image.save('static/uploads/filter_image.png', format='PNG')
    return render_template("index.html", image_path1='static/uploads/original_image.png', image_path2='static/uploads/filter_image.png')

def filtro_laplaciano(imagen):
    # Convertir la imagen a una matriz NumPy en escala de grises
    # Conver L convierte la imagen a escala de grises de 8 bits
    # data type object se escogio 32 bits por cuestion de rendimiento
    # ademas no se necesita demasiada precision en los decimales
    matriz = np.array(imagen.convert("L"), dtype=np.float32)

    # Definimos la máscara del filtro Laplaciano
    # Si es sobel solo cambia la mascara aqui
    mascara = np.array([[0, 1, 0], 
                        [1, -4, 1], 
                        [0, 1, 0]])

    # Aplicamos el filtro Laplaciano a la matriz
    resultado = filtro_convolucion(matriz, mascara)

    # Reescalamos el histograma de la matriz resultante
    resultado_reescalado = reescalar_histograma(resultado)

    # Convertir la matriz resultante reescalada en una imagen PIL
    imagen_resultante = Image.fromarray(resultado_reescalado)

    return imagen_resultante
def filtro_convolucion(matriz, mascara):
    # Obtener el tamaño de la máscara
    # Como es una matriz cuadarada basta el primera valor de la tupla
    size = mascara.shape[0]
    
    # Obtener las dimensiones de la matriz
    altura, ancho = matriz.shape

    # Crear una matriz vacía para almacenar el resultado
    resultado = np.zeros_like(matriz)

    # Aplicar el filtro convolucional

    # Para cada y 
    for y in range(altura):
        # Para cada x
        for x in range(ancho):
            suma = 0

            for i in range(size):
                for j in range(size):
                    # Coordenadas del píxel vecino
                    vecino_x = x + j - size // 2
                    vecino_y = y + i - size // 2

                    # Verificar si el píxel vecino está dentro de los límites de la matriz
                    if 0 <= vecino_x < ancho and 0 <= vecino_y < altura:
                        suma += matriz[vecino_y][vecino_x] * mascara[i][j]

            resultado[y][x] = suma

    return resultado

def reescalar_histograma(histograma):
    # Encontrar el valor máximo y mínimo en el histograma
    max_val = np.max(histograma)
    min_val = np.min(histograma)

    # Reescalar el histograma al rango de 0 a 255
    # Teniendo como puntos(min;0) y (max;2^bits-1)
    # m= ((2^bits-1)-0)/(max_val-min_val)
    # histograma_reescalado=m*(histograma-min_val)
    # histograma_reescalado=((2^bits-1)-0)/(max_val-min_val)*(histograma-min_val)
    # histograma_reescalado=(2^bits-1)*(histograma-min_val)/(max_val-min_val)
    # Se usa 8 bits por pixel entones el factor seria 255
    histograma_reescalado = ((histograma - min_val) / (max_val - min_val)) * 255
    

    # Convertir el histograma reescalado a enteros de 8 bits sin signo
    histograma_reescalado = histograma_reescalado.astype(np.uint8)

    return histograma_reescalado



def apply_filter(image, selected_filter):
    if selected_filter == "median":
        return image.filter(ImageFilter.MedianFilter())
    elif selected_filter == 'boxblur':
        return image.filter(ImageFilter.BoxBlur(5))
    elif selected_filter == 'laplacian':
        return filtro_laplaciano(image)
    return None
@app.route("/about")
def about():
    return render_template("about.html")
if __name__ == "__main__":
    app.run(debug=True)
