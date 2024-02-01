import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import tkintermapview
from gps import get_coordinates_from_folder

class FourFrameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Three Frames Display")
        self.root.state('zoomed')
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_left_frame()
        self.create_middle_frame()
        self.create_right_frame()

    def create_left_frame(self):
        self.left_frame = tk.Frame(self.main_frame, width=100, borderwidth=1, relief="solid")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create Listbox widget in the left frame
        self.listbox = tk.Listbox(self.left_frame)
        self.listbox.pack(fill=tk.BOTH, expand=True)

        # Bind listbox selection event
        self.listbox.bind("<<ListboxSelect>>", self.on_image_selected)

    def create_middle_frame(self):
        self.middle_frame = tk.Frame(self.main_frame, width=400, borderwidth=1, relief="solid")
        self.middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.top_middle_frame = tk.Frame(self.middle_frame, height=300, width=400, bd=2, relief="solid")
        self.top_middle_frame.pack(fill='both', expand=True)

        self.middle_middle_frame = tk.Frame(self.middle_frame, height=100, width=400, bd=2, relief="solid")
        self.middle_middle_frame.pack(fill='both', expand=True)

        self.bottom_middle_frame = tk.Frame(self.middle_frame, height=300, width=400, bd=2, relief="solid")
        self.bottom_middle_frame.pack(fill='both', expand=True)

    def create_right_frame(self):
        self.right_frame = tkintermapview.TkinterMapView(self.main_frame, width=600, corner_radius=0)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def populate_listbox(self):
        self.folder_path = self.select_folder()
        if self.folder_path:
            if os.path.exists(self.folder_path):
                self.add_marker(self.folder_path)
                image_files = [f for f in os.listdir(self.folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                if image_files:
                    for image_file in image_files:
                        self.listbox.insert(tk.END, image_file)
                else:
                    self.show_popup("No Image Files Found", "No image files found in the specified folder.")
            else:
                self.show_popup("Folder Not Found", "The specified folder does not exist.")
        else:
            self.show_popup("No Device Found", "No connected device found.")

    def on_image_selected(self, event):
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_image = self.listbox.get(selected_index[0])
            image_path = os.path.join(self.folder_path, selected_image)
            self.display_image(image_path)

    def display_image(self, image_path):
        image = Image.open(image_path)

        # Fixed size for top_middle_frame
        fixed_width = 400
        fixed_height = 300

        # Resize the image to fit within the fixed size of top_middle_frame
        resized_image = image.resize((fixed_width, fixed_height), Image.ANTIALIAS)

        # Create a PhotoImage object for the resized image
        photo = ImageTk.PhotoImage(resized_image)

        # Destroy existing labels in top_middle_frame
        for label in self.top_middle_frame.winfo_children():
            label.destroy()

        # Display the resized image in top_middle_frame
        label = tk.Label(self.top_middle_frame, image=photo)
        label.photo = photo  # Keep a reference to the image to prevent it from being garbage collected
        label.pack(fill='both', expand=True)


    def select_folder(self):
        self.folder_path = filedialog.askdirectory(title="Select Folder")
        return self.folder_path

    def add_marker(self,folder_path):
        coord = get_coordinates_from_folder(folder_path)
        marker = []
        i = 0
        for img,coords in coord.items():
                marker.append(self.right_frame.set_marker(coords[0],coords[1]))
                i += 1
        j = 0

        path = []
        while j<i-1:
            path.append(self.right_frame.set_path([marker[j].position,marker[j+1].position]))
            j += 1

    def show_popup(self, title, message):
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry("300x100")
        tk.Label(popup, text=message, padx=20, pady=20).pack()
        tk.Button(popup, text="OK", command=popup.destroy).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = FourFrameGUI(root)
    app.populate_listbox()  # Automatically populate the listbox on startup
    root.mainloop()