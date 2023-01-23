import customtkinter
from utils import vrp
import random
import pickle
from tkintermapview import TkinterMapView
import osmnx as ox
import networkx as nx
from threading import Thread
from multiprocessing import Process, Manager, Queue
import time
import sys
'''
    TODO : 
        1. Get current city and traffic data.
        2. Add depot and delivery location icon in markers.
        3. Multi Depot VRPy OSMnx Combination
'''
def l(val=None):
    start_time = time.perf_counter()
    print('Start loading Map Graph.')

    #val.extend(ox.load_graphml("Dhaka.graphml"))
    with open('Dhaka.pickle', 'rb') as handle:
        #val.extend([pickle.load(handle)])
        data = pickle.load(handle)
    print(f'Done loading Map Graph in {time.perf_counter() - start_time} seconds.')
    return data

class App(customtkinter.CTk):

    APP_NAME = "TSP GUI"
    WIDTH = 800
    HEIGHT = 500

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.G = None
        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)
        #self.bind("<<Foo>>", self.doFoo)
        self.depot_locations = None
        self.depot_marker = None
        self.delivery_locations = []
        self.delivery_markers = []
        self.paths = []
        self.progress_bar_flag = None
        self.q = Queue()
        self.add_widgets()
        Thread(target=self.load_data).start()

    def add_widgets(self):
        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

        # ============ frame_left ============

        self.frame_left.grid_rowconfigure(2, weight=1)

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,text="Calculate Optimal Routes",command=self.calculate_route, state='disabled')
        self.button_1.grid(pady=(10, 10), padx=(10, 10), row=0, column=0, sticky='nsew')
        self.progress_bar = customtkinter.CTkProgressBar(master=self.frame_left)
        self.progress_bar.set(0)
        self.progress_bar.grid(pady=(10, 10), padx=(10, 10), row=1, column=0)
        self.button_2 = customtkinter.CTkButton(master=self.frame_left, text="Clear Markers", command=self.clear_marker_event)
        self.button_2.grid(pady=(20, 0), padx=(20, 20), row=2, column=0, sticky='sew')

        self.map_label = customtkinter.CTkLabel(self.frame_left, text="Tile Server:", anchor="w")
        self.map_label.grid(row=4, column=0, padx=(20, 20), pady=(20, 0))
        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=["Google normal", "Google satellite", "OpenStreetMap"], command=self.change_map)
        self.map_option_menu.grid(row=5, column=0, padx=(20, 20), pady=(10, 0))

        self.appearance_mode_label = customtkinter.CTkLabel(self.frame_left, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=(20, 20), pady=(20, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left, values=["Light", "Dark", "System"], command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=(20, 20), pady=(10, 20))

        # ============ frame_right ============

        self.frame_right.grid_rowconfigure(0, weight=1)
        
        self.frame_right.grid_rowconfigure(1, weight=0)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=0)
        self.frame_right.grid_columnconfigure(2, weight=0)

        self.map_widget = TkinterMapView(self.frame_right, corner_radius=0)
        self.map_widget.grid(row=0, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(0, 0), pady=(0, 0))
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.map_widget.add_right_click_menu_command(label="Set Depot Location", command=self.set_depot_location, pass_coords=True)
        self.map_widget.add_right_click_menu_command(label="Set Delivery Location", command=self.set_delivery_location, pass_coords=True)

        self.entry = customtkinter.CTkEntry(master=self.frame_right, placeholder_text="type address")
        self.entry.grid(row=1, column=0, rowspan=1, sticky="we", padx=(12, 0), pady=12)
        self.entry.bind("<Return>", self.search_event)

        self.button_5 = customtkinter.CTkButton(master=self.frame_right,
                                                text="Search",
                                                width=90,
                                                command=self.search_event)
        self.button_5.grid(row=1, column=1, sticky="e", padx=(12, 12), pady=12)

        # Set default values
        self.map_widget.set_address("Dhaka")
        self.map_widget.set_zoom(12)
        #self.map_option_menu.set("OpenStreetMap")
        self.appearance_mode_optionemenu.set("System")

    def load_data(self):
        self.progress_bar.configure(mode='indeterminate')
        self.progress_bar.start()

        # print("Starting Map Data loading")
        #with Manager() as m:
        #    val = m.list()
        #    p1 = Process(target=l, args=(val,))
        #    p1.start()
        #    p1.join()
        #self.G = val
        self.G = l()
        print(self.G)

        # print('Done loading Map Graph.')
        self.button_1.configure(state='normal')
        self.progress_bar.configure(mode='determinate')
        self.progress_bar.stop()
        self.progress_bar.set(0)

    def calculate_route(self, event=None):
        if not (self.depot_locations and self.delivery_locations):
            return
        self.progress_bar.configure(mode='indeterminate')
        self.progress_bar.start()

        Thread(target=self.run_vrp).start()

    def run_vrp(self):
        p = Process(target=vrp, args=[self.G, self.depot_locations, self.delivery_locations, self.q])
        p.start()
        p.join()
        self.progress_bar.configure(mode='determinate')
        self.progress_bar.stop()
        self.progress_bar.set(1)

        r = lambda: random.randint(0,255)
        while self.q:
            shortest_route_by_distance = self.q.get()
            route = [[float(self.G.nodes[node]['y']), float(self.G.nodes[node]['x'])]for node in shortest_route_by_distance]
            self.paths.append(self.map_widget.set_path(route, color='#%02X%02X%02X' % (r(),r(),r()), width=6))
    def search_event(self, event=None):
        self.map_widget.set_address(self.entry.get())

    def set_depot_location(self, coordinates):
        #self.depot_markers.append(self.map_widget.set_marker(coordinates[0], coordinates[1], text=f"Depot : {len(self.depot_markers) + 1}"))
        #self.depot_locations.append(coordinates)
        if self.depot_marker is not None:
            self.depot_marker.delete()
        self.depot_marker = self.map_widget.set_marker(coordinates[0], coordinates[1], text="Depot")
        self.depot_locations = [list(coordinates)]

    def set_delivery_location(self, coordinates):
        self.delivery_markers.append(self.map_widget.set_marker(coordinates[0], coordinates[1], text=f"Delivery Location : {len(self.delivery_markers) + 1}"))
        self.delivery_locations.append(list(coordinates))

    def clear_marker_event(self):
        #for marker in self.depot_markers:
            #marker.delete()
        for marker in self.delivery_markers:
            marker.delete()
        self.depot_marker.delete() if self.depot_marker is not None else print("Depot location not set")

        self.depot_location = None
        self.depot_marker = None
        self.delivery_locations = []
        self.delivery_markers = []
        self.progress_bar.configure(mode='determinate')
        self.progress_bar.stop()
        self.progress_bar.set(0)
        self.map_widget.delete_all_path()
        self.map_widget.delete_all_marker()

    def change_appearance_mode(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_map(self, new_map: str):
        if new_map == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif new_map == "Google satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    def on_closing(self, event=0):
        # self.destroy()
        self.quit()
        sys.exit(0)
    def start(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()