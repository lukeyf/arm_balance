
import pandas as pd
import numpy as np
import vl_convert as vlc
import altair as alt
from sklearn.model_selection import GridSearchCV
import mglearn
from decimal import Decimal
from src.utils.metric import *
from sklearn.metrics import make_scorer

def get_data(files, group_size = 10000):
    '''
    Get an aggregated and averaged set of data by random sampling
    
    Parameters
    ----------
    files : List[str]
        a list of file names that contains torque data
    group_size : int, divisible by 10000
        group size of the data you want to take the average
    '''
    return get_all_data(files).groupby('y').agg(
                lambda x: np.average(x.sample(group_size,random_state=123,replace = False),
                             axis=0)).reset_index()

def get_all_data(files:list):
    '''
    Get all data from a list of filenames
    
    Parameters
    ----------
    files : List[str]
        a list of file names that contains torque data
    '''
    df = None
    
    for data in files:
        content = pd.read_csv(data)
        df = pd.concat([df, content])
    return df.iloc[: , 1:]

def save_chart(chart, filename, scale_factor=3):
    '''
    Save an Altair chart using vl-convert
    Credit: Joel Ostblom (MDS)
    
    Parameters
    ----------
    chart : altair.Chart
        Altair chart to save
    filename : str
        The path to save the chart to
    scale_factor: int or float
        The factor to scale the image resolution by.
        E.g. A value of `2` means two times the default resolution.
    '''
    with alt.data_transformers.enable("default"), alt.data_transformers.disable_max_rows():
        if filename.split('.')[-1] == 'svg':
            with open(filename, "w") as f:
                f.write(vlc.vegalite_to_svg(chart.to_dict()))
        elif filename.split('.')[-1] == 'png':
            with open(filename, "wb") as f:
                f.write(vlc.vegalite_to_png(chart.to_dict(), scale=scale_factor))
        else:
            raise ValueError("Only svg and png formats are supported")
        
def format_e(n):
    '''
    to scientific notation
    https://stackoverflow.com/questions/6913532/display-a-decimal-in-scientific-notation
    
    Parameters
    ----------
    n: float
        number
    '''
    a = '%E' % n
    return str(round(float(a.split('E')[0]),2)) + 'E' + a.split('E')[1]
        
    
def display_heatmap(param_grid:dict, pipe, X_train, y_train):
    '''
    cross validate and display a heat map with given pipeline and traing set
    credit: Varada Kolhatkar (UBC MDS)
    
    Parameters
    ----------
    param_grid : dict
        Grid of parameters to search
    pipe : sklearn.pipeline.Pipeline
        The path to save the chart to
    X_train: pandas.DataFrame
        The features
    y_train: pandas.Series
        The target
    '''
    grid_search = GridSearchCV(
        pipe, param_grid, cv=len(y_train.unique()), n_jobs=-1,
            scoring=make_scorer(scoring, greater_is_better=False)
    )
    grid_size = [len(data) for data in param_grid.values()]
    grid_search.fit(X_train, y_train)
    results = pd.DataFrame(grid_search.cv_results_)
    scores = np.array(results.mean_test_score).reshape(*grid_size)

    # plot the mean cross-validation scores
    mglearn.tools.heatmap(
        scores,
        xlabel="gamma",
        xticklabels=[format_e(g) for g in param_grid["svr__gamma"]],
        ylabel="C",
        yticklabels=[format_e(c) for c in param_grid["svr__C"]],
        cmap="viridis",
    )
    return grid_search