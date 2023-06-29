import requests
import json, os

SEPARATOR = '######################################################'
# These apply to all prompts
ADDITIVES = ', neon++ green++, high quality, professional, dramatic, very detailed, focused, '
NEGATIVES = 'white border, man, woman, people, person, car, cars, city, squished, squashed, distorted eyes, blurry eyes, poorly drawn hands, extra limbs, gross proportions, missing arms, mutated hands, long neck, duplicate, mutilated hands, poorly drawn face, deformed, bad anatomy, cloned face, malformed limbs, missing legs, too many fingers, ugly, tiling, out of frame, mutation, extra legs, extra arms, disfigured, deformed, cross-eye, body out of frame, blurry, bad art, bad anatomy, blurred, text, watermark, grainy, writing, calligraphy, sign, signature, logo, cut off, bad proportions'

# These only apply when the word is present and adds "++" as a suffix
EMPHASIS = ['hazmat', 'sewers', 'tunnels', 'carousel', 'labyrinth', 'radioactive', 'sewage', 'fields', 'post-apocalyptic', 'theme park']

def create_images(stable_key, transcript_file):
    # url = "https://stablediffusionapi.com/api/v3/text2img"
    url = "https://stablediffusionapi.com/api/v4/dreambooth"

    with open(transcript_file, "r") as file:
        data = json.load(file)

        transcript = data['result']

        paragraphs = transcript.splitlines()
        
        print(len(paragraphs))
        for idx, paragraph in enumerate(paragraphs):
            modified = paragraph.lower()
            for word in EMPHASIS:
                modified = modified.replace(word, word+'++')
            
            # use this array for rerunning failed images
            # ids = [2]
            # if idx in ids:

            # This will process all paragraphs in the lore
            if idx > -1:
                print(idx)
                print(modified)
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

                headers = {
                'Content-Type': 'application/json'
                }

                response = requests.request("POST", url, headers=headers, data=payload)
                print(response.text)
                jsonObj = json.loads(response.text)
                # print(jsonObj)
                print(jsonObj['output'])
                print('\n' + SEPARATOR + '\n')
                if jsonObj['output'] != None and len(jsonObj['output']) > 0:
                    imageUrl = jsonObj['output'][0]
                    r = requests.get(imageUrl, allow_redirects=True)

                    open('./images/image{0}.png'.format(idx), 'wb').write(r.content)
