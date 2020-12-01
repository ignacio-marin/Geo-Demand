import matplotlib.pyplot as plt

def plot_circles(ax, center, radius):
    ax.plot(center[0], center[1],'r+')
    for i in range(1,5):
        circle = plt.Circle(center, radius=i*radius, fill=False, color='k', alpha=0.4)
        ax.add_artist(circle)

def plot_scatter_coordinates(df, x, y, z, center='', radius=''):
    """
    Plots a 2D scatter 
    """
    ax = df.plot.scatter(x, y, c=z, colormap='hsv')
    if center and radius:
        plot_circles(ax, center, radius)
    ax.plot()
    plt.show()