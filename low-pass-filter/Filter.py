import numpy as np
from scipy.signal import butter, lfilter, freqz
import matplotlib.pyplot as plt
import csv
import tkinter as tk
import matplotlib
matplotlib.use('TkAgg')

from matplotlib.figure import Figure

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)

class App(tk.Tk): 
    def __init__(self):
        super().__init__()
        self.geometry("300x300")
        self.title("Low Pass Filter csv data")
        self.t = []
        self.filteredData = []
        tk.Label(self, text="Filename").pack()
        self.textbox = tk.Entry(self)
        self.textbox.pack()
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

        self.openButton = tk.Button(self, text="Plot Data", command = lambda: self.openFile())
        self.openButton.pack()
        self.saveButton = tk.Button(self, text="Save Filtered Data", command = lambda: self.saveData())
        self.saveButton.pack()
        
        
        # Default Values
        self.orderEntry.insert(0, '2')
        self.fsEntry.insert(0, '30')
        self.cutoffEntry.insert(0, '0.1')
        self.offsetEntry.insert(0, '0')
        
    def openFile(self):
        plt.clf()
        filename = self.textbox.get()
        order = int(self.orderEntry.get())
        fs = int(self.fsEntry.get())
        cutoff = float(self.cutoffEntry.get())
        offset = float(self.offsetEntry.get())

        realData = []
        self.t = []
        data = []
        try:
            with open(filename + ".csv") as csv_file:
              csv_reader = csv.reader(csv_file, delimiter=',')
              line_count = 0
              for row in csv_reader:
                # x, y data
                realData.append((row[0], row[1]))
                self.t.append(float(row[0]))
                data.append(float(row[1]))
              print(f'Processed {line_count} lines.')
        except:
            tk.messagebox.showerror('Could not read file', 'File was not found or able to be opened')
            return
              
        b, a = self.butter_lowpass(cutoff, fs, order)
        # Plotting the frequency response.
        
        w, h = freqz(b, a, worN=8000)
        
        plt.subplot(2, 1, 1)
        plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')
        plt.plot(cutoff, 0.5*np.sqrt(2), 'ko')
        plt.axvline(cutoff, color='k')
        plt.xlim(0, 0.5*fs)
        plt.title("Lowpass Filter Frequency Response")
        plt.xlabel('Frequency [Hz]')
        plt.grid()
        
        # Creating the data for filteration
        T = self.t[-1] - self.t[0]
        n = len(realData)

        # Filtering and plotting
        self.filteredData = self.butter_lowpass_filter(data, cutoff, fs, order)

        # Offset the filtered data
        self.offsetTime = []
        for x in self.t: 
          self.offsetTime.append(x-offset)
        

        plt.subplot(2, 1, 2)
        plt.plot(self.t, data, 'b-', label='data', linewidth=1)
        plt.plot(self.offsetTime, self.filteredData, 'g-', linewidth=1, label='filtered data')
        plt.xlabel('Time [ms]')
        plt.grid()
        plt.legend()

        plt.subplots_adjust(hspace=0.35)
        plt.show()
        
          
    def butter_lowpass(self, cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def butter_lowpass_filter(self, data, cutoff, fs, order=5):
        b, a = self.butter_lowpass(cutoff, fs, order=order)
        y = lfilter(b, a, data)
        return y
    
    def saveData(self):
        plt.clf()
        filename = self.textbox.get()
        order = self.orderEntry.get()
        fs = self.fsEntry.get()
        cutoff = self.cutoffEntry.get()
        
        if(len(self.filteredData) == 0):
            tk.messagebox.showerror('Could not save', 'Please plot the file first')
            return
        
        #Output file name
        file = open(f'filtered_({order}_{fs}_{cutoff}){filename}.csv', 'w')
        writer = csv.writer(file)
        
        for i in range(len(self.filteredData)):
            writer.writerow([self.offsetTime[i], self.filteredData[i]])
        file.close()
        
        
        

if __name__ == '__main__':
    app = App()
    app.mainloop()
        
        