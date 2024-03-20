from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
from datetime import datetime


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

def get_date_taken(exif_data):
    if not exif_data:
        return None

    for tag, value in exif_data.items():
        tag_name = TAGS.get(tag, tag)
        if tag_name == 'DateTimeOriginal':
            try:
                date_taken = datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                return date_taken.date()
            except ValueError:
                pass

    return None

def get_coordinates_from_folder(folder_path):
    image_coordinates = {}
    image_dates = {}

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                image_path = os.path.join(root, file)
                image = Image.open(image_path)
                exif_data = image._getexif()
                coordinates = get_coordinates(image_path)
                date_taken = get_date_taken(exif_data)
                
                if coordinates:
                    image_coordinates[file] = coordinates
                if date_taken:
                    image_dates[file] = date_taken

    return image_coordinates, image_dates

def get_exif_data(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if exif_data:
            exif_dict = {}
            for tag, value in exif_data.items():
                if not isinstance(value, bytes):  # Exclude hex values
                    tag_name = TAGS.get(tag, tag)
                    exif_dict[tag_name] = value
            return exif_dict
        else:
            return {}
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return {}



def get_exif_data_from_folder(folder_path):
    image_exif_data = {}

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                image_path = os.path.join(root, file)
                exif_data = get_exif_data(image_path)
                if exif_data:
                    image_exif_data[file] = exif_data

    return image_exif_data

