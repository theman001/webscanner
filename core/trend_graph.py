def plot_trend(dates, values, title, ylabel, filename):
    import matplotlib.pyplot as plt  # heavy import; deferred so runs that skip trend graphs stay fast

    plt.figure()
    plt.plot(dates, values, marker="o")
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
