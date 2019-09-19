''' Create a simple stocks correlation dashboard.

Choose stocks to compare in the drop down widgets, and make selections
on the plots to update the summary and histograms accordingly.

.. note::
    Running this example requires downloading sample data. See
    the included `README`_ for more information.

Use the ``bokeh serve`` command to run the example by executing:

    bokeh serve stocks

at your command prompt. Then navigate to the URL

    http://localhost:5006/stocks

.. _README: https://github.com/bokeh/bokeh/blob/master/examples/app/stocks/README.md

'''
try:
    from functools import lru_cache
except ImportError:
    # Python 2 does stdlib does not have lru_cache so let's just
    # create a dummy decorator to avoid crashing
    print ("WARNING: Cache for this example is available on Python 3 only.")
    def lru_cache():
        def dec(f):
            def _(*args, **kws):
                return f(*args, **kws)
            return _
        return dec

from os.path import dirname, join

import pandas as pd

from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import PreText, Select
from bokeh.plotting import figure

DEFAULT_TICKERS = ['IDM', 'POSTIDM', 'ALL']

def nix(val, lst):
    return [x for x in lst if x != val]

datadict = {'IDM':'dummyIDM.pkl','POSTIDM':'dummyIDM.pkl','ALL':'dummyPOSTIDM.pkl'}
datafolder = './bokeh-app/data/'
@lru_cache()
def load_ticker(ticker):
    datafile = datafolder + datadict[ticker]
    return pd.read_pickle(datafile)

@lru_cache()
def get_data(t1):
    data = load_ticker(t1)
    data = data.dropna()
    print (data.columns)
    print (data.shape[0])
    return data

# set up widgets

stats = PreText(text='', width=500)
ticker1 = Select(value='IDM', options=nix('IDM', DEFAULT_TICKERS))

# set up plots

source = ColumnDataSource(data=dict(x=[], y=[]))
source_static = ColumnDataSource(data=dict(x=[], y=[]))
tools = 'pan,wheel_zoom,xbox_select,reset'

corr = figure(plot_width=350, plot_height=350,
              tools='pan,wheel_zoom,box_select,reset')
corr.circle('centerx', 'centery', size=2, source=source,
            selection_color="orange", alpha=0.6, nonselection_alpha=0.1, selection_alpha=0.4)

# ts1 = figure(plot_width=900, plot_height=200, tools=tools, x_axis_type='datetime', active_drag="xbox_select")
# ts1.line('date', 't1', source=source_static)
# ts1.circle('date', 't1', size=1, source=source, color=None, selection_color="orange")

# ts2 = figure(plot_width=900, plot_height=200, tools=tools, x_axis_type='datetime', active_drag="xbox_select")
# ts2.x_range = ts1.x_range
# ts2.line('date', 't2', source=source_static)
# ts2.circle('date', 't2', size=1, source=source, color=None, selection_color="orange")

# set up callbacks

def ticker1_change(attrname, old, new):
    ticker2.options = nix(new, DEFAULT_TICKERS)
    update()

def ticker2_change(attrname, old, new):
    ticker1.options = nix(new, DEFAULT_TICKERS)
    update()

def update(selected=None):
    t1 = ticker1.value

    data = get_data(t1)
    source.data = source.from_df(data[['centerx', 'centery']])
    source_static.data = source.data

    update_stats(data, t1)

#    corr.title.text = '%s returns vs. %s returns' % (t1, t2)
#    ts1.title.text, ts2.title.text = t1, t2

def update_stats(data, t1):
#    stats.text = str(data[[t1]].describe())
    stats.text = str(data[["ene1","sigma"]].describe())

ticker1.on_change('value', ticker1_change)

def selection_change(attrname, old, new):
    t1 = ticker1.value
    data = get_data(t1)
    selected = source.selected.indices
    if selected:
        data = data.iloc[selected, :]
    update_stats(data, t1)

source.selected.on_change('indices', selection_change)

#set up layout
widgets = column(ticker1, stats)
main_row = row(corr, widgets)
#series = column(ts1)
layout = column(main_row)

# initialize
update()

curdoc().add_root(layout)
curdoc().title = "Stocks"
