import zlib, json
from PIL import Image
import numpy as np

class Img2MapTopo:
    def __init__(self, img_path, tile_mapping, save_version=13, width=5, height=5, show_image=False):
        self.save_version = save_version
        self.width = width
        self.height = height
        self.tile_map = list(tile_mapping.keys())
        self.tile_array = []
        self.tile_amounts = []
        self.tile_mapping = tile_mapping
        self.show_image = show_image
        
        self.target_size = (width * 64, height * 64)

        pixel_matrix = self.image_to_matrix(img_path)
        self.matrix_to_map(pixel_matrix)

    def quantize_colors(self, image):

        color_array = []
        for key, value in BASE_MAPPING.items():
            color_array.extend([list(color) for color in value])

        # Convert array of pixels to a numpy array
        colors = np.array(color_array)

        # Convert image to numpy array
        img_arr = np.array(image)

        # Compute the distance between each pixel and the representative colors
        dist = np.linalg.norm(img_arr[:, :, np.newaxis, :] - colors, axis=-1)

        # Find the index of the closest representative color for each pixel
        closest_color_index = np.argmin(dist, axis=-1)

        # Map the index to the representative color
        quantized_image = colors[closest_color_index]

        return Image.fromarray(quantized_image.astype(np.uint8))

    def image_to_matrix(self, image_path):
        # Open the image file
        image = Image.open(image_path).convert("RGB")
        
        # Resize the image to the target size
        image_resized = image.resize(self.target_size)

        # Flip the image to match worldbox format
        flipped_image = image_resized.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
        
        # Quantize the image to 16 colors
        quantized_image = self.quantize_colors(flipped_image)
        
        # Display the image to the user
        if self.show_image:
            quantized_image.rotate(180).transpose(Image.FLIP_LEFT_RIGHT).show()
        
        # Convert the quantized image to a matrix
        pixel_data = list(quantized_image.getdata())
        
        # Convert pixel data to a matrix
        width, height = quantized_image.size
        pixel_matrix = []

        for pixel in pixel_data:
            for tile_map in self.tile_mapping:
                if pixel in self.tile_mapping[tile_map]:
                    pixel_matrix.append(self.tile_map.index(tile_map))
        
        return [pixel_matrix[i * width:(i + 1) * width] for i in range(height)]

    def matrix_to_map(self, matrix):
        tile_array = []
        tile_amounts = []

        for row in matrix:
            first = row[0]
            cur_row_array = [first]
            cur_row_amount = []
            cur_count = 0
            for c in row:
                if c != first:
                    first = c
                    cur_row_array.append(first)
                    cur_row_amount.append(cur_count)
                    cur_count = 1
                else:
                    cur_count += 1
            cur_row_amount.append(cur_count)
            tile_array.append(cur_row_array)
            tile_amounts.append(cur_row_amount)
        
        self.tile_array = tile_array
        self.tile_amounts = tile_amounts

    def to_dict(self):
        return {
            "saveVersion": self.save_version,
            "width": self.width,
            "height": self.height,
            "mapStats": {},
            "worldLaws":{},
            "tileMap": self.tile_map,
            "tileArray": self.tile_array,
            "tileAmounts": self.tile_amounts,
        }

    def save(self, path):
        with open(path, "wb") as f:
            f.write(zlib.compress(json.dumps(self.to_dict()).encode()))

BASE_MAPPING = {
    "mountains": [(59, 42, 24)],
    "hills": [(103, 91, 76), (38, 26, 11)],
    "soil_high": [(139, 115, 80), (112, 115, 71), (195, 177, 157)],
    "soil_low": [(62, 97, 61)],
    "close_ocean": [(100, 157, 181)],
    "deep_ocean": [(66, 91, 112), (15, 28, 44), (65, 84, 94)]
}

# Change Below Here!!
# image_path = 'italy.tif'
image_path = '.\\images\\europe.PNG'

# update the base mapping if you are using a different site
img2map = Img2MapTopo(image_path, BASE_MAPPING, width=7, height=5, show_image=True)

# change the path where you want to save the wbox file
img2map.save("map.wbox")