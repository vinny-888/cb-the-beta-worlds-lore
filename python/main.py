from stable_diffusion import create_images

# API Key from https://stablediffusionapi.com/
stable_key = ''

# Location of the lore to process
transcript_file = './transcript/2.json'

def main():
    print('Running Image Generation')
    create_images(stable_key, transcript_file)

main()