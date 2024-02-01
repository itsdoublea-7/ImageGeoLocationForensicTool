from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os

def dms_to_dd(degrees, minutes, seconds, direction):
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60)
    if direction in ['S', 'W']:
        dd *= -1
    return dd

def get_geotagging(exif):
    if not exif:
        raise ValueError("No EXIF metadata found")

    geotagging = {}
    for (idx, tag) in TAGS.items():
        if tag == 'GPSInfo':
            if idx not in exif:
                raise ValueError("No EXIF geotagging found")

            for (key, val) in GPSTAGS.items():
                if key in exif[idx]:
                    geotagging[val] = exif[idx][key]

    return geotagging

def get_coordinates(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if exif_data is not None:
            geotagging = get_geotagging(exif_data)
            if geotagging:
                latitude_dms = geotagging.get('GPSLatitude')
                longitude_dms = geotagging.get('GPSLongitude')

                if latitude_dms and longitude_dms:
                    latitude = dms_to_dd(*latitude_dms, geotagging.get('GPSLatitudeRef', ''))
                    longitude = dms_to_dd(*longitude_dms, geotagging.get('GPSLongitudeRef', ''))

                    return latitude, longitude
                else:
                    return None
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return None

def get_coordinates_from_folder(folder_path):
    image_coordinates = {}
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                image_path = os.path.join(root, file)
                coordinates = get_coordinates(image_path)
                if coordinates:
                    image_coordinates[image_path] = coordinates

    return image_coordinates

# Example usage
folder_path = "image"
result = get_coordinates_from_folder(folder_path)
print(result)
for image_path, coordinates in result.items():
    print(f"Image: {image_path}\nCoordinates: {coordinates}\n")
