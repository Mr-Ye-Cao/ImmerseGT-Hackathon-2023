from flask import Flask, request, jsonify
import requests
import json
import logging
from dalle_api import generate_dalle_image
from PIL import Image
import io
import os

import base64

import torch
from io import BytesIO
import transformers
from diffusers import StableDiffusionImg2ImgPipeline

from clip_api import image_similarity

# Configure logging
logging.basicConfig(filename='request_logs.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

#device = "cuda"
model_id_or_path = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_id_or_path, torch_dtype=torch.float32)
#pipe = pipe.to(device)

app = Flask(__name__)

# listen for http://127.0.0.1:5000/api_call
@app.route('/api_call', methods=['POST'])
def api_call():
    # Determine the type of request
    if request.get_json():
        input_data = request.get_json()
        if 'request_type' in input_data:
            request_type = input_data['request_type']
        elif input_data.get('request type'):
            request_type = input_data.get('request type')
        logging.info(f"Received request data: {json.dumps(input_data, indent=2)}")
    elif request.form:
        request_type = request.form.get('request type')
    

    if request_type == 'dall-e generate challenge image':
        logging.info(f"request type: dall-e generate challenge image")

        # extract dall-e prompt
        dall_e_text_prompt = input_data.get("request content")

        # Call the function with a prompt
        image_url = generate_dalle_image(dall_e_text_prompt)

        logging.info(f"the image generated by dall-e is at: {image_url}")

        return jsonify({'image_url': image_url}), 200



    elif request_type == 'stable diffusion generate image given image and text prompt':
        logging.info(f"request type: stable diffusion generate user image")


        # url = "https://raw.githubusercontent.com/CompVis/stable-diffusion/main/assets/stable-samples/img2img/sketch-mountains-input.jpg"

        # response = requests.get(url)
        # init_image = Image.open(BytesIO(response.content)).convert("RGB")
        # init_image = init_image.resize((768, 512))

        # prompt = "A fantasy landscape, trending on artstation"

        # images = pipe(prompt=prompt, image=init_image, strength=0.75, guidance_scale=7.5).images
        # images[0].save("fantasy_landscape.png")

        

        # extract prompt
        text_prompt = input_data['text_prompt']

        print("text_prompt from stable diffusion")
        print(text_prompt)

        # extract user image

        encoded_image = input_data['encoded_image']

        # Decode the base64 encoded image
        init_image = base64.b64decode(encoded_image)


        # Generate image using stable diffusion
        init_image = Image.open(BytesIO(init_image))
        init_image = init_image.resize((768, 512))

        images = pipe(prompt=text_prompt, image=init_image, strength=0.75, guidance_scale=7.5).images

        print(f"Stable diffusion generated {len(images)} images")

        images[0].save("generated.png")


        return 'Image saved successfully', 200



    elif request_type == 'clip compares similarity between dall-e image and user image':
        logging.info(f"request type: clip judges results")

        # extract dall-e image
                    # Access the two images sent by the client
        dalle_image = request.files.get('dalle_image')
        
        # extract user's image
        user_image = request.files.get('user_image')


        # Save the images to the desired folder
        dalle_image.save(f"/Users/yecao/Desktop/imgt/ImmerseGT-Hackathon-2023/Bandend-Server/temp/{dalle_image.filename}")
        user_image.save(f"/Users/yecao/Desktop/imgt/ImmerseGT-Hackathon-2023/Bandend-Server/temp/{user_image.filename}")

        # use clip for cosine distance
        # dalle_image = Image.open(BytesIO(dalle_image)).convert("RGB")
        # user_image = Image.open(BytesIO(user_image)).convert("RGB")

        similar_score = image_similarity(f"/Users/yecao/Desktop/imgt/ImmerseGT-Hackathon-2023/Bandend-Server/temp/{dalle_image.filename}",
                         f"/Users/yecao/Desktop/imgt/ImmerseGT-Hackathon-2023/Bandend-Server/temp/{user_image.filename}")
    
        print(f"the similarity score is {similar_score}")

    else:
        logging.info(f"request type: undefined")
        



    # Return a simple response
    return jsonify({'message': 'Request received and logged'}), 200

if __name__ == '__main__':
    app.run(debug=True)
