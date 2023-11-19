import requests
import os
import base64
import io
from PIL import Image

api_url = "http://localhost:80/inpaint"

def b64s(imgfile):
    with open(imgfile, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

# payload = {
#     # "prompt": "Robot sitting on a bench",
#     # "prompt": "Create a highly detailed and realistic image of a plain white cotton T-shirt. The T-shirt should be displayed in a neutral setting with natural lighting, emphasizing its simplicity and classic design. The fabric texture should be clearly visible, showcasing the soft, natural cotton fibers, with subtle creases and folds to suggest a lightweight and breathable material. The T-shirt should have a standard round neckline and short sleeves, with a clean and seamless appearance. The overall look should be one of pristine cleanliness and unworn freshness, embodying the quintessential casual garment. Focus on the precision of the stitching along the hem, sleeves, and neckline, highlighting the quality craftsmanship.",
#     # "prompt": "highly realistic, very detailed, brown young man standing in kitchen in front of oven wearing a clean bright white T-shirt, natural lighting, white T-shirt, clear white fabric, natural folds, simple white T-shirt, classic white T-shirt",
#     # "prompt": "highly detailed, very realistic, A man stands in a kitchen with wood cabinets and an oven, smiling while wearing a simple white cotton T-shirt with a round neckline. He sports clear glasses, a watch on his left wrist, and holds his hands together. A clear glass bottle sits on the countertop behind him.",
#     # "prompt": "highly detailed, very realistic, brown young man standing in kitchen in front of oven wearing a clean bright white T-shirt. The T-shirt is simple and the folds are natural. The fit emphasizes its simplicity and classic design. The fabric texture should be clearly visible, showcasing the soft cotton",
#     # "prompt": "a plain white cotton T-shirt, fitting comfortably with a relaxed demeanor, short sleeves, and a soft texture evident in the fabric.",
#     # "prompt": "Create a highly detailed and realistic image of a white button-up shirt paired with a tie. The shirt should be presented in a formal setting, with crisp and clean lighting that highlights its sophisticated design. The fabric of the shirt should have a subtle texture, indicating a high-quality cotton blend, with sharp, precise folds and a well-ironed appearance. Each button should be distinct and aligned perfectly down the front of the shirt. The collar should be stiff and neatly pointed, laying flat and framing the tie. The tie should be of a contrasting color, perhaps a deep navy or rich burgundy, with a sleek, silk-like sheen and a classic diagonal striped pattern. The knot of the tie should be a perfect Windsor knot, sitting snugly against the shirt's collar. The shirt's sleeves should have precise, adjustable cufflinks, and the overall fit of the shirt should suggest a tailored, professional look.",
#     # "prompt": "A well-pressed, clean, white button-up shirt paired with a sleek, simple solid black tie. The shirt should have a crisp collar, neatly buttoned cuffs, and a smooth, unblemished surface. The tie is matte black, with a classic, narrow design, tied neatly around the collar of the shirt.",
#     # "prompt": "A plain red t-shirt featuring a distinct white horizontal stripe across the chest. The shirt is the focal point of the image, with no background details mentioned. The fabric of the t-shirt looks soft and comfortable, with a smooth texture. The white stripe is clean and crisp, contrasting sharply against the vibrant red of the shirt. The t-shirt is displayed in a way that highlights its design and color.",
#     # "prompt": "A vibrant, sports jersey with the iconic Red Bull logo prominently displayed on the chest. The jersey is primarily in dark blue and silver colors, featuring dynamic, energetic design patterns that evoke a sense of speed and agility. The sleeves are short, with a comfortable, athletic fit. Red accents are visible around the collar and the edges of the sleeves, adding a striking contrast to the blue and silver. The fabric appears high-quality and breathable, suitable for athletic activities. The Red Bull logo is detailed, with the two bulls facing each other against a yellow sun background",
#     #"prompt": "Montreal Canadiens Jersey",
#     "prompt": "Argentina soccer jersey",
#     "img": b64s("santoshOG.png"),
#     "mask": b64s("backend/huggingface-cloth-segmentation/output/alpha/1.png")
# }
# # files = {
# #     'img': ('santoshOG.png', open('santoshOG.png', 'rb'), 'image/png'),
# #     'mask': ('mask.png', open('mask.png', 'rb'), 'image/png')
# # }
# response = requests.post(api_url, json=payload)
# image_filename = "filledimage.jpg"
# with open(image_filename, "wb") as f:
#     f.write(response.content)
# # print(response)
# # print(response.status_code)
# # print(response.content)
# # print(response.text)
# # print(response.headers)

# response = requests.post("http://localhost:80/seg", json={"img": b64s("santoshOG.png")})
# im = Image.open(io.BytesIO(base64.b64decode(response.json()["img"])))
# im.show()

res = requests.post("http://localhost:80/main", json={"img": b64s("testimage.png"), "prompt": "Montreal Canadiens Jersey"})
im = Image.open(io.BytesIO(base64.b64decode(res.json()["img"])))
im.show()