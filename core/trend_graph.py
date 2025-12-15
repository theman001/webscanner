import matplotlib.pyplot as plt

def plot_trend(dates, values, title, ylabel, filename):
    plt.figure()
    plt.plot(dates, values, marker="o")
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
