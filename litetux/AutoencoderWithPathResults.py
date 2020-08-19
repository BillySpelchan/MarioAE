import matplotlib.pyplot as plt

class AutoencoderWithPathResults:
    def __init__(self):
        pass

    def load_results_csv(self, csv_file_name):
        tests = []
        for _ in range(8):
            tests.append([[],[],[]])
        with open(csv_file_name, 'r') as csv:
            for line in csv:
                data = line.split(',')
                #name, id, map,error,gnd_err,pct_wrong,groundvsskyerr

                try:
                    pathtype = int(data[1].strip())
                    mapid = int(data[2].strip())
                    bad = float(data[5].strip())
                except ValueError:
                    print("Invalid line in csv: ", data)
                    continue
                tests[pathtype][mapid].append(bad)
        return tests


    def generate_box_plot(self, plot_title, csv_file_name, col_start=1, col_end=7, mapid = 0, out_file=None):
        csv_data = self.load_results_csv(csv_file_name)
        plot_data = []
        for cntr in range(col_start, col_end+1):
            plot_data.append(csv_data[cntr][mapid])
        plt.clf()
        plt.boxplot(plot_data)
        plt.title(plot_title)
        plt.xlabel("Method")
        plt.ylabel("Error rate")

        if out_file is not None:
            plt.savefig(out_file, dpi=600)
        else:
            plt.show()


p = AutoencoderWithPathResults()
for m in range(3):
    #p.generate_box_plot("test", "path_test.csv", 0, 6, m, None)#"mario_paths_encoding.png")
    #p.generate_box_plot("test", "path_test.csv", 0, 6, m, "mario_paths_encoding"+str(m)+".png")
    p.generate_box_plot("Predict Map " + str(m+1), "predict_full.csv", 0, 6, m, None)
    p.generate_box_plot("Predict Map " + str(m+1), "path_test.csv", 0, 6, m, "mario_predict_encoding"+str(m)+".png")
