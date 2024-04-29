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
    img = img.point(lambda x: 0 if x < 128 else 255)
    img = img.resize((img.width * 2, img.height * 2))
    text = pytesseract.image_to_string(img)
    #print(text)
    return text

import re

def analyze_text(text):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are standardizing the text from a receipt."},
            {"role": "user", "content": "Standardize the following text, using the following format Item: [item_name, type: string], Quantity: [quantity, type: int], ignoring pricing information, focusing only on item name and quantity. Ignore any item name that sounds like gibberish " + text}
        ]
    )

    standardized_text = completion.choices[0].message.content

    # Use a regular expression to extract item names and quantities
    matches = re.findall(r'Item: \[(.*?)\], Quantity: \[(\d+)\]', standardized_text)

    # Convert matches to a list of dictionaries
    items = [{"item_name": item, "quantity": int(quantity)} for item, quantity in matches]

    return items

if __name__ == '__main__':
    text = parse_text_from_image('IMG_5610.png')
    print(text)

    #print("why is this running multiple times")
    #print(analyze_text(text))