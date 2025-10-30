from tkinter import Frame, Label, Entry, Button, StringVar, Tk

class InputForm(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        self.label_axis = Label(self, text="Enter Axis Information:")
        self.label_axis.grid(row=0, column=0, columnspan=2)

        self.label_point = Label(self, text="Enter Point Coordinates (x, y):")
        self.label_point.grid(row=1, column=0)

        self.entry_point = Entry(self)
        self.entry_point.grid(row=1, column=1)

        self.label_tunnel = Label(self, text="Enter Tunnel Dimensions (length, height):")
        self.label_tunnel.grid(row=2, column=0)

        self.entry_tunnel = Entry(self)
        self.entry_tunnel.grid(row=2, column=1)

        self.submit_button = Button(self, text="Submit", command=self.submit)
        self.submit_button.grid(row=3, column=0, columnspan=2)

    def submit(self):
        point_data = self.entry_point.get()
        tunnel_data = self.entry_tunnel.get()
        # Here you would typically process the input data
        print(f"Point Data: {point_data}, Tunnel Data: {tunnel_data}")

def main():
    root = Tk()
    root.title("Road Axis Input Form")
    app = InputForm(master=root)
    app.pack()
    root.mainloop()

if __name__ == "__main__":
    main()