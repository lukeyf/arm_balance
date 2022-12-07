import numpy as np
def scoring(X,y):
    '''
    The scoring metric to evaluate the model's performance
    Calculates the max error of predicted values and actual values
    
    Parameters
    ----------
    X : np.array
        a list of predicted values
    y : np.array
        a list of actual targets
    '''
    return np.mean(np.abs(X-y))
