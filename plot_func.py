import matplotlib.pyplot as plt

def plot_circles(ax, center, radius_lst):
    ax.plot(center[0], center[1],'r+')
    for r in radius_lst:
        circle = plt.Circle(center, 
                            radius=r, 
                            fill=False, 
                            color='k', 
                            alpha=0.6,
                            linestyle='--')
        ax.add_artist(circle)

def plot_scatter_coordinates(df, x, y, z, center=None, radius=[]):
    """
    Plots a 2D scatter 
    """
    ax = df.plot.scatter(x, y, c=z, colormap='Paired', alpha=0.4)
    if center and radius.any():
        plot_circles(ax, center, radius)
    ax.plot()
    plt.show()