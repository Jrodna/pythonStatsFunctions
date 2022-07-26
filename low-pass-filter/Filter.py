import numpy as np
from scipy.signal import butter, lfilter, freqz
import matplotlib.pyplot as plt
import csv
import tkinter as tk
import matplotlib

matplotlib.use("TkAgg")
import os
from tkinter import filedialog as fd


class App(tk.Tk):
    def __init__(self):

        super().__init__()
        self.geometry("500x400")
        self.title("Low Pass Filter csv data")

        self.plotData = {}

        self.t = []
        self.filteredData = []
        self.filePaths = []

        tk.Button(self, text="Select Files", command=lambda: self.selectFiles()).pack()

        self.filenamesLabel = tk.Label(self, text="\n".join(self.filePaths))
        self.filenamesLabel.pack()

        tk.Label(self, text="order (whole number > 0)").pack()
        self.orderEntry = tk.Entry(self)
        self.orderEntry.pack()
        tk.Label(self, text="fs (Hz) > 1").pack()
        self.fsEntry = tk.Entry(self)
        self.fsEntry.pack()
        tk.Label(self, text="cutoff (Hz) 0-1").pack()
        self.cutoffEntry = tk.Entry(self)
        self.cutoffEntry.pack()

        tk.Label(self, text="x axis offset").pack()
        self.offsetEntry = tk.Entry(self)
        self.offsetEntry.pack()

        self.openButton = tk.Button(self, text="Plot Data", command=lambda: self.plotGraphs())
        self.openButton.pack()
        self.saveButton = tk.Button(self, text="Save Filtered Data", command=lambda: self.saveData())
        self.saveButton.pack()

        # Default Values
        self.orderEntry.insert(0, "2")
        self.fsEntry.insert(0, "30")
        self.cutoffEntry.insert(0, "0.1")
        self.offsetEntry.insert(0, "0")

    def selectFiles(self):
        self.filePaths = fd.askopenfilenames(filetypes=[("CSC files", "*.csv")])
        filenames = []
        for filePath in self.filePaths:
            path, filename = os.path.split(filePath)
            filenames.append(filename)

        self.filenamesLabel.config(text="\n".join(filenames))

    def plotGraphs(self):
        plt.clf()
        self.order = int(self.orderEntry.get())
        self.fs = int(self.fsEntry.get())
        self.cutoff = float(self.cutoffEntry.get())
        self.offset = float(self.offsetEntry.get())
        totalGraphs = len(self.filePaths) + 1

        b, a = self.butter_lowpass(self.cutoff, self.fs, self.order)
        # Plotting the frequency response.
        w, h = freqz(b, a, worN=8000)

        plt.subplot(totalGraphs, 1, 1)
        plt.plot(0.5 * self.fs * w / np.pi, np.abs(h), "b")
        plt.plot(self.cutoff, 0.5 * np.sqrt(2), "ko")
        plt.axvline(self.cutoff, color="k")
        plt.xlim(0, 0.5 * self.fs)
        plt.title("Lowpass Filter Frequency Response")
        plt.xlabel("Frequency [Hz]")
        plt.grid()

        pos = 2

        print(totalGraphs, pos)
        for filePath in self.filePaths:
            self.openFile(filePath, pos, totalGraphs)
            pos += 1
        plt.subplots_adjust(hspace=1, top=0.95, bottom=0.05)
        plt.show()

    def openFile(self, filePath, position, totalGraphs):

        path, filename = os.path.split(filePath)
        realData = []
        t = []
        data = []
        try:
            with open(filePath) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=",")
                line_count = 0
                for row in csv_reader:
                    # x, y data
                    try:
                        x = float(row[0])
                        y = float(row[1])
                        t.append(x)
                        data.append(y)
                        realData.append((row[0], row[1]))
                    except ValueError:
                        print('row is not numerical data')
                    line_count += 1
                print(f"Processed {line_count} lines.")
        except:
            tk.messagebox.showerror("Could not read file", "File was not found or able to be opened")
            return

        # Creating the data for filteration
        T = t[-1] - t[0]
        n = len(realData)

        # Filtering and plotting
        filteredData = self.butter_lowpass_filter(data, self.cutoff, self.fs, self.order)

        # Offset the filtered data
        offsetTime = []
        for x in t:
            offsetTime.append(x - self.offset)

        self.plotData[filename] = {"x": offsetTime, "y": filteredData}

        plt.subplot(totalGraphs, 1, position)
        plt.plot(t, data, "b-", label="data", linewidth=1)
        plt.plot(self.plotData[filename]["x"], self.plotData[filename]["y"], "g-", linewidth=1, label="filtered data")
        plt.title(filename)
        plt.xlabel("Time [ms]")
        plt.grid()
        plt.legend()

        plt.subplots_adjust(hspace=0.35)

    def butter_lowpass(self, cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype="low", analog=False)
        return b, a

    def butter_lowpass_filter(self, data, cutoff, fs, order=5):
        b, a = self.butter_lowpass(cutoff, fs, order=order)
        y = lfilter(b, a, data)
        return y

    def saveData(self):
        plt.clf()

        directory = fd.askdirectory()

        if directory == "":
            print("cancelled")
            return

        for filePath in self.filePaths:
            path, filename = os.path.split(filePath)

            if len(self.plotData[filename]["y"]) == 0:
                tk.messagebox.showerror("Could not save", "Please plot the file first")
                return

            # Output file name
            file = open(
                f"{directory}/filtered_({self.order}_{self.fs}_{self.cutoff}_{self.offset}){filename}",
                "w",
                newline="",
            )
            writer = csv.writer(file)

            for i in range(len(self.plotData[filename]["y"])):
                writer.writerow([self.plotData[filename]["x"][i], self.plotData[filename]["y"][i]])
            file.close()


if __name__ == "__main__":
    app = App()
    app.mainloop()
