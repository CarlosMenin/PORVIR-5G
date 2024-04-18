import csv
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

base_filename = 'teste/my5grantester-iperf-1-{}-{}-{}.csv'
execs = [ 1, 2, 4, 6, 8, 10 ]
cores = [1]
cores_name = ['Open5GS']

interval = 6
bits_per_second_avg = 8

MAX_AXIS_X = 2
MAX_AXIS_Y = 3

for core_idx, core in enumerate(cores):

    axis_x = 0
    axis_y = 0
    figure, axis = plt.subplots(MAX_AXIS_X, MAX_AXIS_Y)
    figure.canvas.manager.set_window_title(cores_name[core_idx])

    for exe in execs:
        all_avg_throughput = np.array([])
        for exp in range(0, exe):
            timestamp = np.array([])
            throughput = np.array([])
            avg_throughput = np.array([])

            with open(base_filename.format(core, exe, exp), newline='') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    try:
                        interval = int(float(row[list(row.keys())[6]].split('-')[1]))
                        curr_throughput = float(row[list(row.keys())[8]]) / 1000000
                        if interval in timestamp:
                            avg_throughput = np.repeat(curr_throughput, throughput.size)
                            all_avg_throughput = np.append(all_avg_throughput, curr_throughput)
                            continue

                        throughput = np.append(throughput, curr_throughput)
                        timestamp = np.append(timestamp, interval)
                    except Exception as e:
                        print (e)
                        continue

            if throughput.size > 0:
                # Get color
                sns.set_palette("husl")

                axis[axis_x, axis_y].plot(timestamp, throughput, label = "#UE {} (exec {})".format(exe, exp))
                axis[axis_x, axis_y].plot(timestamp, avg_throughput, label = "AVG #UE {} (exec {})".format(exe, exp))
                # axis[axis_x, axis_y].legend()
                #axis[axis_x, axis_y].set_prop_cycle(None)

        num_ues = all_avg_throughput.size
        sum_avg_throughput = np.sum(all_avg_throughput)
        axis[axis_x, axis_y].set_title("#UE {}/{} (Sum avg: {:.2f})".format(num_ues, exe, sum_avg_throughput))
        axis_y += 1
        if axis_y == MAX_AXIS_Y:
            axis_y = 0
            axis_x += 1

    plt.show()

