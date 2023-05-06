from flask import Flask, request, render_template
from PIL import Image, ImageFilter

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
            original_image.save('static/img/original_image.png', format='PNG')
        except Exception as e:
            error_message = f"Error: {str(e)}"
            return render_template("index.html", error_message=error_message)

    if original_image is None:
        return render_template("index.html", error_message="Please upload an image first.")

    filtered_image = apply_filter(original_image, filter)
    if filtered_image is None:
        return render_template("index.html", error_message="Invalid filter selected.")

    filtered_image.save('static/img/filter_image.png', format='PNG')
    return render_template("index.html", image_path1='static/img/original_image.png', image_path2='static/img/filter_image.png')

def apply_filter(image, selected_filter):
    if selected_filter == "median":
        return image.filter(ImageFilter.MedianFilter())
    elif selected_filter == 'boxblur':
        return image.filter(ImageFilter.BoxBlur(5))
    elif selected_filter == 'laplacian':
        # Agrega aquí la lógica correspondiente para el filtro 'laplacian'
        pass
    return None

if __name__ == "__main__":
    app.run(debug=True)
