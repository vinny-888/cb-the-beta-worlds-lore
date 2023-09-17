import requests
import json, os
import time
SEPARATOR = '######################################################'
# These apply to all prompts
# ADDITIVES = ', neon++ green++, high quality, professional, dramatic, very detailed, focused, '
# NEGATIVES = 'white border, man, woman, people, person, car, cars, city, squished, squashed, distorted eyes, blurry eyes, poorly drawn hands, extra limbs, gross proportions, missing arms, mutated hands, long neck, duplicate, mutilated hands, poorly drawn face, deformed, bad anatomy, cloned face, malformed limbs, missing legs, too many fingers, ugly, tiling, out of frame, mutation, extra legs, extra arms, disfigured, deformed, cross-eye, body out of frame, blurry, bad art, bad anatomy, blurred, text, watermark, grainy, writing, calligraphy, sign, signature, logo, cut off, bad proportions'
ADDITIVES = 'landscape, buildings, interior, no people, radioactive, ooze, carnival, high quality, professional, dramatic, very detailed, focused, post-apocalyptic, '
# NEGATIVES = 'white border, man, woman, people, person, car, cars, city, squished, squashed, distorted eyes, blurry eyes, poorly drawn hands, extra limbs, gross proportions, missing arms, mutated hands, long neck, duplicate, mutilated hands, poorly drawn face, deformed, bad anatomy, cloned face, malformed limbs, missing legs, too many fingers, ugly, tiling, out of frame, mutation, extra legs, extra arms, disfigured, deformed, cross-eye, body out of frame, blurry, bad art, bad anatomy, blurred, text, watermark, grainy, writing, calligraphy, sign, signature, logo, cut off, bad proportions'
NEGATIVES = 'ghouls, ghosts, portrait, man, woman, people, person, car, cars, city, blurred, text, watermark, sign, signature, logo'

# These only apply when the word is present and adds "++" as a suffix
EMPHASIS = ['no people', 'sewer', 'tunnel', 'carousel', 'labyrinth', 'radioactive', 'sewage', 'fields', 'theme park']

def create_images(stable_key, transcript_file):
    # url = "https://stablediffusionapi.com/api/v3/text2img"
    # url = "https://stablediffusionapi.com/api/v4/dreambooth"
    url = "https://cloud.leonardo.ai/api/rest/v1/generations"
    # curl --request POST \
    #  --url https://cloud.leonardo.ai/api/rest/v1/generations \
    #  --header 'accept: application/json' \
    #  --header 'authorization: Bearer 59d46808-d44f-4a41-9601-43109e1e66b3' \
    #  --header 'content-type: application/json' \
    #  --data '

    with open(transcript_file, "r") as file:
        data = json.load(file)

        transcript = data['result']

        paragraphs = transcript.splitlines()
        
        print(len(paragraphs))
        offset = 69
        paragraphs = paragraphs[offset:]

        # shortArr = [paragraphs[0]]
        for idx, paragraph in enumerate(paragraphs):
            modified = paragraph.lower()
            modified = modified.replace(' fuck', '')
            modified = modified.replace(' flesh', '')
            for word in EMPHASIS:
                modified = modified.replace(word, word+'++')
            
            # use this array for rerunning failed images
            # ids = [2]
            # if idx in ids:

            # This will process all paragraphs in the lore
            if idx > -1:
                print(idx)
                print(modified)

                use_sd = False
                if use_sd:
                    payload = json.dumps({
                    "key": stable_key,
                    "prompt": ADDITIVES + modified,
                    "negative_prompt": NEGATIVES,
                    "width": "512",
                    "height": "512",
                    "samples": "1",
                    "num_inference_steps": "20",
                    "seed": None,
                    "guidance_scale": 7.5,
                    "safety_checker": "yes",
                    "multi_lingual": "no",
                    "panorama": "no",
                    "self_attention": "no",
                    "upscale": "no",
                    "model_id":"synthwave-diffusion",
                    # "embeddings_model": "embeddings_model_id",
                    "webhook": None,
                    "track_id": None
                    })
                else:             
                    payload = json.dumps({
                        "height": 512,
                        "modelId": "ac614f96-1082-45bf-be9d-757f2d31c174",
                        "prompt": ADDITIVES + modified,
                        "negative_prompt": NEGATIVES,
                        "width": 768,
                        "alchemy": False,
                        "num_images": 1,
                        "promptMagic": False,
                        "public": True,
                        "contrastRatio": 0.5,
                        "expandedDomain": True,
                        "guidance_scale": 15,
                        "highContrast": False,
                        "highResolution": False,
                        "imagePromptWeight": 0.45,
                        "init_strength": 0.55,
                        "nsfw": False,
                        "num_inference_steps": 10,
                        "photoReal": False,
                        "presetStyle": "NONE",
                        "tiling": False,
                        "weighting": 1
                    })

                headers = {
                    'Content-Type': 'application/json',
                    'accept': 'application/json',
                    'authorization': 'Bearer API_KEY'
                }

                response = requests.request("POST", url, headers=headers, data=payload)
                print(response.text)
                jsonObj = json.loads(response.text)
                # print(jsonObj)

                if use_sd:
                    print(jsonObj['output'])
                    print('\n' + SEPARATOR + '\n')
                    if jsonObj['output'] != None and len(jsonObj['output']) > 0:
                        imageUrl = jsonObj['output'][0]
                        r = requests.get(imageUrl, allow_redirects=True)

                        open('./images/image{0}.png'.format(idx), 'wb').write(r.content)
                else:
                    if jsonObj['sdGenerationJob'] != None:
                        genId = jsonObj['sdGenerationJob']['generationId']
                        gotImage = False
                        while not gotImage:
                            print('Trying to get image!')
                            time.sleep(10)
                            # curl --request GET \
                            #     --url https://cloud.leonardo.ai/api/rest/v1/generations/524d6e2e-11df-4cfc-97ce-d7c1c984d0d1 \
                            #     --header 'accept: application/json' \
                            #     --header 'authorization: Bearer 59d46808-d44f-4a41-9601-43109e1e66b3'
                            response2 = requests.request("GET", 'https://cloud.leonardo.ai/api/rest/v1/generations/'+genId, headers=headers)

                            print(response2.text)
                            jsonObj = json.loads(response2.text)
                            if jsonObj['generations_by_pk'] != None:
                                if len(jsonObj['generations_by_pk']['generated_images']) > 0:
                                    print('Got image!')
                                    imageUrl = jsonObj['generations_by_pk']['generated_images'][0]['url']
                                    #  "generations_by_pk": {
                                    #     "generated_images": [
                                    #     {
                                    #         "url":

                                    r = requests.get(imageUrl, allow_redirects=True)

                                    open('./images/image{0}.png'.format(idx+offset), 'wb').write(r.content)

                                    gotImage = True
