import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import tkintermapview
from geopy.geocoders import Nominatim
from gps import get_coordinates_from_folder, get_exif_data_from_folder
from tkcalendar import DateEntry  
import pickle

class FourFrameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image GPS Forensics Tool")
        self.root.state('zoomed')
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.marker = []
        self.path = []
        self.address = {}
        self.exifdata = {}
        self.geolocator = Nominatim(user_agent="geoapiExcercises")
        self.coord = {}
        self.dates = {}
        self.states = {}
        self.image_files = []

        self.create_menu()
        self.create_left_frame()
        self.create_middle_frame()
        self.create_right_frame()
    
    def set_map_style(self, tile_server_url, max_zoom=None):
        self.right_frame.set_tile_server(tile_server_url, max_zoom)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New Session", command=self.new_session)
        filemenu.add_command(label="Load Session", command=self.load_session)
        filemenu.add_command(label="Save Session", command=self.save_session)
        menubar.add_cascade(label="File", menu=filemenu)

        filtermenu = tk.Menu(menubar, tearoff=0)
        filtermenu.add_command(label="Filter using Date", command=self.filter_images)
        filtermenu.add_command(label="Filter by Location", command=self.location_filter)
        filtermenu.add_command(label="Clear Filter", command=self.clear_filter)
        menubar.add_cascade(label="Filter", menu=filtermenu)

        map_style_menu = tk.Menu(menubar, tearoff=0)
        map_style_menu.add_command(label="OpenStreetMap", command=lambda: self.set_map_style("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"))
        map_style_menu.add_command(label="Google Normal", command=lambda: self.set_map_style("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22))
        map_style_menu.add_command(label="Google Satellite", command=lambda: self.set_map_style("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22))
        menubar.add_cascade(label="Map Style", menu=map_style_menu)

        self.root.config(menu=menubar)

    def location_filter(self):
        unique_city = set(self.states.values())
        filter_popup = tk.Toplevel(self.root)
        filter_popup.title("Location Filter")

        state_label = tk.Label(filter_popup, text="Select State:")
        state_label.grid(row=0, column=0, padx=5, pady=5)

        state_var = tk.StringVar()
        state_var.set("")  # Default to empty string
        state_listbox = tk.Listbox(filter_popup, listvariable=state_var, height=10)
        state_listbox.grid(row=0, column=1, padx=5, pady=5)

        for state in sorted(unique_city):
            state_listbox.insert(tk.END, state)

        def apply_location_filter():
            selected_state = state_listbox.get(state_listbox.curselection())
            if selected_state:
                filtered_images = [img for img, state in self.states.items() if state == selected_state]
                self.listbox.delete(0, tk.END)
                for image in filtered_images:
                    self.listbox.insert(tk.END, image)
                filter_popup.destroy()        
        
        filter_button = tk.Button(filter_popup, text="Apply", command=apply_location_filter)
        filter_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    def new_session(self):
        self.listbox.delete(0, tk.END)
        self.right_frame.delete_all_marker()
        self.right_frame.delete_all_path()
        self.marker = []
        self.path = []
        self.address = {}
        self.exifdata = {}
        self.coord = {}
        self.dates = {}
        self.states = {}
        self.populate_listbox()

    def load_session(self):
        self.listbox.delete(0, tk.END)
        self.right_frame.delete_all_marker()
        self.right_frame.delete_all_path()
        file_path = filedialog.askopenfilename(title="Load Session", filetypes=[("Session files", "*.session")])
        if file_path:
            with open(file_path, 'rb') as file:
                session_data = pickle.load(file)
            self.address = session_data['address']
            self.exifdata = session_data['exifdata']
            self.coord = session_data['coord']
            self.dates = session_data['dates']
            self.image_files = session_data['image_files']
            self.folder_path = session_data['folder_path']
            self.states = session_data['states']
            for image_file in self.image_files:
                        self.listbox.insert(tk.END, image_file)
            self.add_marker_load()

    def save_session(self):
        session_data = {
            'address': self.address,
            'exifdata': self.exifdata,
            'coord': self.coord,
            'dates': self.dates,
            'image_files': self.image_files,
            'folder_path': self.folder_path,
            'states': self.states
        }
        file_path = filedialog.asksaveasfilename(defaultextension=".session", filetypes=[("Session files", "*.session")])
        if file_path:
            with open(file_path, 'wb') as file:
                pickle.dump(session_data, file)

    def create_left_frame(self):
        self.left_frame = tk.Frame(self.main_frame, width=100, borderwidth=1, relief="solid")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(self.left_frame)
        self.listbox.pack(fill=tk.BOTH, expand=True)

        self.listbox.bind("<<ListboxSelect>>", self.on_image_selected)

    def create_middle_frame(self):
        self.middle_frame = tk.Frame(self.main_frame, width=400, borderwidth=1, relief="solid")
        self.middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.top_middle_frame = tk.Frame(self.middle_frame, height=300, width=400, bd=2, relief="solid")
        self.top_middle_frame.pack(fill="both", expand=True)

        self.middle_middle_frame = tk.Frame(self.middle_frame, height=300, width=400, bd=2, relief="solid")
        self.middle_middle_frame.pack(fill="both", expand=True)
        self.address_label = tk.Label(self.middle_middle_frame, wraplength=400)
        self.address_label.pack(fill="x",expand=True)

        self.bottom_middle_frame = tk.Frame(self.middle_frame, height=200, width=400, bd=2, relief="solid")
        self.bottom_middle_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.bottom_middle_frame, borderwidth=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.bottom_middle_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.scrollable_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def create_right_frame(self):
        self.right_frame = tkintermapview.TkinterMapView(self.main_frame, width=600, corner_radius=0)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def populate_listbox(self):
        self.folder_path = self.select_folder()
        if self.folder_path:
            if os.path.exists(self.folder_path):
                self.add_marker(self.folder_path)
                self.image_files = [f for f in os.listdir(self.folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                if self.image_files:
                    for image_file in self.image_files:
                        self.listbox.insert(tk.END, image_file)
                else:
                    self.show_popup("No Image Files Found", "No image files found in the specified folder.")
            else:
                self.show_popup("Folder Not Found", "The specified folder does not exist.")
        else:
            self.show_popup("No Device Found", "No connected device found.")        

    def update_properties(self, exif_data):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for row, (tag, value) in enumerate(exif_data.items()):
            tag_label = tk.Label(self.scrollable_frame, text=tag, anchor="w", padx=5, pady=2, borderwidth=1, relief="solid")
            tag_label.grid(row=row, column=0, sticky="ew")

            value_label = tk.Label(self.scrollable_frame, text=value, anchor="w", wraplength=300, justify="left", padx=5, pady=2, borderwidth=1, relief="solid")
            value_label.grid(row=row, column=1, sticky="ew")

    def on_image_selected(self, event):
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_image = self.listbox.get(selected_index[0])
            image_path = os.path.join(self.folder_path, selected_image)
            self.display_image(image_path)
            self.address_label.config(text=self.address[selected_image])
            coords = self.coord[selected_image]
            self.right_frame.set_position(coords[0], coords[1])
            self.right_frame.set_zoom(16)
            self.update_properties(self.exifdata[selected_image])

    def show_image_popup(self, image_path):
        image = Image.open(image_path)
        image.show()

    def display_image(self, image_path):
        image = Image.open(image_path)
        fixed_width = 400
        fixed_height = 300
        resized_image = image.resize((fixed_width, fixed_height), Image.LANCZOS)
        photo = ImageTk.PhotoImage(resized_image)
        for label in self.top_middle_frame.winfo_children():
            label.destroy()
        label = tk.Label(self.top_middle_frame, image=photo)
        label.photo = photo
        label.pack(fill='both', expand=True)
        label.bind("<Button-1>", lambda event: self.show_image_popup(image_path))


    def filter_images(self):
        def apply_filter():
            start_date = start_date_entry.get_date()
            end_date = end_date_entry.get_date()
            filtered_images = [image for image, date in self.dates.items() if start_date <= date <= end_date]
            self.listbox.delete(0, tk.END)
            for image in filtered_images:
                self.listbox.insert(tk.END, image)
            filter_popup.destroy()
        filter_popup = tk.Toplevel(self.root)

        start_date_label = tk.Label(filter_popup, text="Start Date:")
        start_date_label.grid(row=0, column=0, padx=5, pady=5)
        start_date_entry = DateEntry(filter_popup)
        start_date_entry.grid(row=0, column=1, padx=5, pady=5)

        end_date_label = tk.Label(filter_popup, text="End Date:")
        end_date_label.grid(row=1, column=0, padx=5, pady=5)
        end_date_entry = DateEntry(filter_popup)
        end_date_entry.grid(row=1, column=1, padx=5, pady=5)

        filter_button = tk.Button(filter_popup, text="Apply Filter", command=apply_filter)
        filter_button.grid(row=2, columnspan=2, padx=5, pady=5)
    
    def clear_filter(self):
        self.listbox.delete(0, tk.END)
        for image in self.dates.keys():
            self.listbox.insert(tk.END, image)

    def select_folder(self):
        self.folder_path = filedialog.askdirectory(title="Select Folder")
        return self.folder_path

    def add_marker_load(self):
        i = 0
        for img, coords in self.coord.items():
            self.marker.append(self.right_frame.set_marker(coords[0], coords[1]))
            self.marker[i].set_text(img)
            i += 1
        j = 0
        for img, coords in self.coord.items():
            self.right_frame.set_position(coords[0], coords[1])
            self.right_frame.set_zoom(16)
            break

        while j < i - 1:
            self.path.append(self.right_frame.set_path([self.marker[j].position, self.marker[j + 1].position]))
            j += 1

    def add_marker(self, folder_path):
        self.coord, self.dates = get_coordinates_from_folder(folder_path)
        self.exifdata =  get_exif_data_from_folder(folder_path)
        i = 0
        for img, coords in self.coord.items():
            self.marker.append(self.right_frame.set_marker(coords[0], coords[1]))
            self.marker[i].set_text(img)
            self.address[img] = self.geolocator.reverse((coords[0], coords[1]))
            if self.address[img]:
                raw_address = self.address[img].raw.get('address', {})
                state = raw_address.get('state')
                if state:
                    self.states[img] = state
            i += 1
        j = 0
        for img, coords in self.coord.items():
            self.right_frame.set_position(coords[0], coords[1])
            self.right_frame.set_zoom(16)
            break

        while j < i - 1:
            self.path.append(self.right_frame.set_path([self.marker[j].position, self.marker[j + 1].position]))
            j += 1

    def show_popup(self, title, message):
        messagebox.showinfo(title, message)

if __name__ == "__main__":
    root = tk.Tk()
    app = FourFrameGUI(root)
    root.mainloop()
