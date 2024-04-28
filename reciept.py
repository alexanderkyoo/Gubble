from PIL import Image
import os
from dotenv import load_dotenv
import pytesseract
from openai import OpenAI
from PIL import Image, ImageEnhance, ImageFilter

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_text(image_path):
    img = Image.open(image_path)
    return pytesseract.image_to_string(img)

def parse_text_from_image(image_path):
    img = Image.open(image_path)
    img = img.convert('L')
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)
    # Apply a threshold to the image
    img = img.point(lambda x: 0 if x < 128 else 255)
    # Resize the image to make the text larger
    img = img.resize((img.width * 2, img.height * 2))
    # Use Tesseract to do OCR on the image
    text = pytesseract.image_to_string(img)
    return text

def analyze_text(text):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are standardizing the text from a receipt."},
            {"role": "user", "content": "Standardize the following text, using the following format Item: [item_name], Quantity: [quantity], ignoring pricing information, focusing only on item name and quantity: " + text}
        ]
    )
    return completion.choices[0].message.content

if __name__ == '__main__':
    #print(parse_text_from_image('reciept.png'))
    print("why is this running multiple times")
    #print(analyze_text(parse_text_from_image('reciept.png')))