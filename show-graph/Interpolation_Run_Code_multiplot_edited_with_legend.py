""" A python script to read in a CSV file and plot data for lab XXX"""

# unlike matlab, in python you have to call the functions/modules you
# are going to use:
import csv  # this is the module that can read, write and manipulate csv files
import numpy as np  # the numerical capabilities of python
import matplotlib.pyplot as plt  # for plotting
import glob

# from obspy.core import Trace, Stats, Stream
from scipy import signal

# Set default font size for plots:
font = {"size": 24}
plt.rc("font", **font)
from tkinter import filedialog as fd
import os


def main():

    # put all file names to read in a list.
    files = sorted(fd.askopenfilenames(filetypes=[("CSC files", "*.csv")]))

    # define values:
    labels = ""
    offset = 0
    fig, ax = plt.subplots(figsize=(12, 8))

    # read and plot data in each file:
    for file in files:
        # read in time/amp:
        # print(file)
        # print(file[2:4])
        t, V = readcsvdata(file)

        path, filename = os.path.split(file)

        parts = filename.split("_")

        # create a custom y-label (sample number), based on  file name:
        # labels = labels + str(file[52:55] + " PP")  # fluid
        labels = labels + str(parts[-3])  # pressure

        # Create a list of t to make a 0 line later
        # t_list.append(t)

        # plot in \mu s:
        # plt.plot(t*1e7,V/max(V)+offset)
        plt.plot(t, V, label=labels)
        plt.axis("on")
        ax.legend()

        # offset traces vertically:
        offset = offset
        labels = ""

    # this is very manual to set the pressure values on the y-axis. It
    # depends crucially on the offset value and the files/pressures
    # recorded:
    # ax.set_yticks(np.arange(len(labels)))
    # ax.set_yticklabels(labels)

    plt.xlabel("Time ($\mu$s)")
    plt.ylabel("Pressure (psi)")
    plt.grid()
    # plt.xlim(0,100)
    # plt.savefig(file[2:8]+'.pdf')

    plt.axhline(y=0, color="r", linestyle="-")

    plt.show()


def readcsvdata(filename):
    """function to read csv. Input filename, output floats time
    and amplitude"""
    csv_in = open(filename, "rU")
    myreader = csv.reader(csv_in, delimiter=",")

    x = []
    y = []
    for row in myreader:
        x.append(row[0])
        y.append(row[1])
    x = np.array([float(i) for i in x])
    y = np.array([float(i) for i in y])
    return x, y


# this will actually run the code:
if __name__ == "__main__":
    main()
