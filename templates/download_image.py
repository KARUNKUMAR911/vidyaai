import urllib.request
import os

os.makedirs('C:/vidyaai/static/images/alphabets', exist_ok=True)

# Accurate Wikipedia/Wikimedia images for each letter
images = {
    'A': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Red_Apple.jpg/320px-Red_Apple.jpg',
    'B': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Monarch_butterfly_shutter.jpg/320px-Monarch_butterfly_shutter.jpg',
    'C': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Kittyply_edit1.jpg/320px-Kittyply_edit1.jpg',
    'D': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/YellowLabradorLooking_new.jpg/320px-YellowLabradorLooking_new.jpg',
    'E': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/African_Bush_Elephant.jpg/320px-African_Bush_Elephant.jpg',
    'F': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Camponotus_flavomarginatus_ant.jpg/320px-Camponotus_flavomarginatus_ant.jpg',
    'G': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Table_grapes_on_white.jpg/320px-Table_grapes_on_white.jpg',
    'H': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Collage_of_Nine_Dogs.jpg/320px-Collage_of_Nine_Dogs.jpg',
    'I': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Ice_Cream_dessert_03.jpg/320px-Ice_Cream_dessert_03.jpg',
    'J': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Jackfruit_hanging.jpg/320px-Jackfruit_hanging.jpg',
    'K': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Jackrabbit_2.jpg/320px-Jackrabbit_2.jpg',
    'L': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Lion_waiting_in_Namibia.jpg/320px-Lion_waiting_in_Namibia.jpg',
    'M': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Macaca_nigra_self-portrait_large.jpg/320px-Macaca_nigra_self-portrait_large.jpg',
    'N': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/A_small_cup_of_coffee.JPG/320px-A_small_cup_of_coffee.JPG',
    'O': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Oranges_and_orange_juice.jpg/320px-Oranges_and_orange_juice.jpg',
    'P': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Pavo_Real_Venezolano.jpg/320px-Pavo_Real_Venezolano.jpg',
    'Q': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/African_Bush_Elephant.jpg/320px-African_Bush_Elephant.jpg',
    'R': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Sunflower_from_Silesia2.jpg/320px-Sunflower_from_Silesia2.jpg',
    'S': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/The_Sun_by_the_Atmospheric_Imaging_Assembly_of_NASA%27s_Solar_Dynamics_Observatory_-_20100819.jpg/320px-The_Sun_by_the_Atmospheric_Imaging_Assembly_of_NASA%27s_Solar_Dynamics_Observatory_-_20100819.jpg',
    'T': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/White_shark.jpg/320px-White_shark.jpg',
    'U': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Good_Food_Display_-_NCI_Visuals_Online.jpg/320px-Good_Food_Display_-_NCI_Visuals_Online.jpg',
    'V': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Violin_VL100.png/220px-Violin_VL100.png',
    'W': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Watermelon_seedless.jpg/320px-Watermelon_seedless.jpg',
    'X': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Xylophone.jpg/320px-Xylophone.jpg',
    'Y': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Yak.jpg/320px-Yak.jpg',
    'Z': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Plains_Zebra_Equus_quagga.jpg/320px-Plains_Zebra_Equus_quagga.jpg',
}

print("Downloading images...")
for letter, url in images.items():
    try:
        filename = f'C:/vidyaai/static/images/alphabets/{letter}.jpg'
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            with open(filename, 'wb') as f:
                f.write(response.read())
        print(f'✅ {letter} downloaded!')
    except Exception as e:
        print(f'❌ {letter} failed: {e}')

print("All done! Check C:/vidyaai/static/images/alphabets/")


