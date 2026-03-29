import urllib.request
import os
import time

os.makedirs('C:/vidyaai/static/images/alphabets', exist_ok=True)

# Using DuckDuckGo image CDN and other free sources
images = {
    'A': 'https://upload.wikimedia.org/wikipedia/commons/1/15/Red_Apple.jpg',
    'B': 'https://live.staticflickr.com/7298/9017540231_83f45a3b93_z.jpg',
    'C': 'https://upload.wikimedia.org/wikipedia/commons/b/bb/Kittyply_edit1.jpg',
    'D': 'https://upload.wikimedia.org/wikipedia/commons/2/26/YellowLabradorLooking_new.jpg',
    'E': 'https://upload.wikimedia.org/wikipedia/commons/3/37/African_Bush_Elephant.jpg',
    'F': 'https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg',
    'G': 'https://upload.wikimedia.org/wikipedia/commons/b/bb/Table_grapes_on_white.jpg',
    'H': 'https://upload.wikimedia.org/wikipedia/commons/d/d9/Collage_of_Nine_Dogs.jpg',
    'I': 'https://upload.wikimedia.org/wikipedia/commons/2/2e/Ice_Cream_dessert_03.jpg',
    'J': 'https://upload.wikimedia.org/wikipedia/commons/8/8e/Jackfruit_hanging.jpg',
    'K': 'https://upload.wikimedia.org/wikipedia/commons/e/e7/Jackrabbit_2.jpg',
    'L': 'https://upload.wikimedia.org/wikipedia/commons/7/73/Lion_waiting_in_Namibia.jpg',
    'M': 'https://upload.wikimedia.org/wikipedia/commons/9/94/Macaca_nigra_self-portrait_large.jpg',
    'N': 'https://upload.wikimedia.org/wikipedia/commons/4/45/A_small_cup_of_coffee.JPG',
    'O': 'https://upload.wikimedia.org/wikipedia/commons/4/43/Oranges_and_orange_juice.jpg',
    'P': 'https://upload.wikimedia.org/wikipedia/commons/8/8e/Pavo_Real_Venezolano.jpg',
    'Q': 'https://upload.wikimedia.org/wikipedia/commons/1/1c/Watermelon_seedless.jpg',
    'R': 'https://upload.wikimedia.org/wikipedia/commons/4/41/Sunflower_from_Silesia2.jpg',
    'S': 'https://upload.wikimedia.org/wikipedia/commons/b/b4/The_Sun_by_the_Atmospheric_Imaging_Assembly_of_NASA%27s_Solar_Dynamics_Observatory_-_20100819.jpg',
    'T': 'https://upload.wikimedia.org/wikipedia/commons/3/3b/Royal_Bengal_Tiger_at_rest.jpg',
    'U': 'https://upload.wikimedia.org/wikipedia/commons/6/6d/Good_Food_Display_-_NCI_Visuals_Online.jpg',
    'V': 'https://upload.wikimedia.org/wikipedia/commons/f/f2/Violin_VL100.png',
    'W': 'https://upload.wikimedia.org/wikipedia/commons/1/1c/Watermelon_seedless.jpg',
    'X': 'https://upload.wikimedia.org/wikipedia/commons/6/6f/Xylophone.jpg',
    'Y': 'https://upload.wikimedia.org/wikipedia/commons/3/30/Yak.jpg',
    'Z': 'https://upload.wikimedia.org/wikipedia/commons/e/e3/Plains_Zebra_Equus_quagga.jpg',
}

headers = {
    'User-Agent': 'VidyaAI-Educational-App/1.0 (educational project; contact@vidyaai.in)',
    'Accept': 'image/jpeg,image/png,image/*',
}

print("Downloading images with delay...")
for letter, url in images.items():
    try:
        filename = f'C:/vidyaai/static/images/alphabets/{letter}.jpg'
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            with open(filename, 'wb') as f:
                f.write(response.read())
        print(f'✅ {letter} downloaded!')
        time.sleep(2)  # Wait 2 seconds between each download
    except Exception as e:
        print(f'❌ {letter} failed: {e}')

print("Done!")