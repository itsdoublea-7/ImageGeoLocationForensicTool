import tkinter as tk
import tkintermapview
from gps import get_coordinates_from_folder
# Replace this with your list of coordinates (e.g., from image EXIF data)
root = tk.Tk()
map_view = tkintermapview.TkinterMapView(root, width=600, corner_radius=0)
map_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

folder_path = "image"
coord = get_coordinates_from_folder(folder_path)

marker = []
i = 0
for img,coords in coord.items():
        marker.append(map_view.set_marker(coords[0],coords[1]))
        i += 1
j = 0

path = []
while j<i-1:
    path.append(map_view.set_path([marker[j].position,marker[j+1].position]))
    j += 1
# Create markers for each coordinate
#m1 = map_view.set_marker(37.7749, -122.4194)
#m2 = map_view.set_marker(37.7833, -122.4167)
#m3 = map_view.set_marker(37.7882, -122.4080)

#path_1 = map_view.set_path([m1.position, m2.position])

root.mainloop()
