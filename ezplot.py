"""
A simple drop-in replacement for the matplotlib's object-oriented plotting
behavior. The only functions exported are `figure` and `show` which can be used
as replacements for the `pylab` function of the same name. The resulting figure
and axes objects work as before, but have some additional functionality and
different default styles.
"""

import matplotlib.pyplot as plt

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from matplotlib.projections import register_projection

__all__ = ['figure', 'show']


# FIXME: I don't like doing this because it globally changes whatever plot
# styles or defaults the user may have set. but I'll leave it for now.
plt.rc('lines', linewidth=2.0)
plt.rc('legend', scatterpoints=3)
plt.rc('figure', facecolor='white')
plt.rc('axes', grid=True)
plt.rc('grid', color='k', linestyle='-', alpha=0.2, linewidth=0.5)
plt.rc('axes', color_cycle=[
    (0.21568627450980393, 0.49411764705882355, 0.7215686274509804),
    (0.30196078431372547, 0.6862745098039216, 0.2901960784313726),
    (0.596078431372549, 0.3058823529411765, 0.6392156862745098),
    (1.0, 0.4980392156862745, 0.0),
    (0.6509803921568628, 0.33725490196078434, 0.1568627450980392),
    (0.9686274509803922, 0.5058823529411764, 0.7490196078431373)])


class CustomAxes(Axes):
    name = 'custom_axes'

    def cla(self):
        super(CustomAxes, self).cla()
        self.spines['top'].set_visible(False)
        self.spines['right'].set_visible(False)
        self.xaxis.set_tick_params(direction='out', top=False)
        self.yaxis.set_tick_params(direction='out', right=False)

    def scatter(self, x, y, **kwargs):
        kwargs.setdefault('s', 40)
        kwargs.setdefault('c', 'k')
        kwargs.setdefault('marker', 'o')
        kwargs.setdefault('linewidths', 1.5)
        kwargs.setdefault('facecolors', 'none')
        super(CustomAxes, self).scatter(x, y, **kwargs)

    def plot_banded(self, x, y=None, b1=None, **kwargs):
        if y is None:
            lines = self.plot(x, **kwargs)
        else:
            lines = self.plot(x, y, **kwargs)
        x = lines[0].get_xdata()
        y = lines[0].get_ydata()
        c = lines[0].get_color()
        a = lines[0].get_alpha()
        a = 1.0 if (a is None) else a
        if b1 is None:
            self.fill_between(x, 0, y, color=c, alpha=0.2*a)
        else:
            self.fill_between(x, y-b1, y+b1, color=c, alpha=0.2*a)

    def axvline(self, x=0, ymin=0, ymax=1, **kwargs):
        kwargs.setdefault('color', 'r')
        kwargs.setdefault('linestyle', '--')
        super(CustomAxes, self).axvline(x, ymin, ymax, **kwargs)

    def axhline(self, y=0, xmin=0, xmax=1, **kwargs):
        kwargs.setdefault('color', 'r')
        kwargs.setdefault('linestyle', '--')
        super(CustomAxes, self).axhline(y, xmin, xmax, **kwargs)


# register the new axes. for some reason this isn't defined to return the class
# object, so we can't use it as a decorator.
register_projection(CustomAxes)


class CustomFigure(Figure):
    """
    A custom figure object which by default creates axes which use the
    'custom_axes' projection. It also adds additional kwargs and methods, but
    if these are ignored the figure acts as a standard matplotlib instance.
    """
    def __init__(self, *args, **kwargs):
        tight_layout = kwargs.pop('tight_layout', True)
        super(CustomFigure, self).__init__(*args, **kwargs)
        self.set_tight_layout(tight_layout)

    def add_subplot(self, *args, **kwargs):
        kwargs.setdefault('projection', 'custom_axes')
        hidex = kwargs.pop('hidex', False)
        hidey = kwargs.pop('hidey', False)
        ax = super(CustomFigure, self).add_subplot(*args, **kwargs)
        if hidex:
            plt.setp(ax.get_xticklabels(), visible=False)
            plt.setp(ax.get_xaxis().get_offset_text(), visible=False)
        if hidey:
            plt.setp(ax.get_yticklabels(), visible=False)
            plt.setp(ax.get_yaxis().get_offset_text(), visible=False)
        return ax

    def add_subplotspec(self, shape, loc, rowspan=1, colspan=1, **kwargs):
        s1, s2 = shape
        subplotspec = GridSpec(s1, s2).new_subplotspec(loc, rowspan, colspan)
        return self.add_subplot(subplotspec, **kwargs)


def figure(*args, **kwargs):
    kwargs.setdefault('FigureClass', CustomFigure)
    return plt.figure(*args, **kwargs)


def show(block=None):
    block = (not plt.isinteractive()) if (block is None) else block
    plt.show(block)
