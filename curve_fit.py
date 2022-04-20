import numpy as np
from scipy.optimize import curve_fit, differential_evolution
import pandas as pd
import warnings

def func(t, a, b, k):
    return a*t + b*(1 - np.exp(-k*t))

# function for genetic algorithm to minimize (sum of squared error)
def sumOfSquaredError(parameterTuple, *args):
    xData, yData = args
    warnings.filterwarnings('ignore')
    val = func(xData, *parameterTuple)
    return np.sum((yData - val) ** 2.0)


def generate_Initial_Parameters(xData, yData):
    # min and max used for bounds
    maxX = max(xData)
    maxY = max(yData)

    parameterBounds = []
    parameterBounds.append([-maxX,maxX]) # search bounds for a
    parameterBounds.append([-maxY,maxY]) # search bounds for b
    parameterBounds.append([0,1]) # search bounds for k

    # "seed" the numpy random number generator for repeatable results
    result = differential_evolution(sumOfSquaredError, parameterBounds, args=(xData, yData), seed=0)
    return result.x

def fit_to_model(df, column1, column2):
    xData, yData = df[column1], df[column2]
    # generate initial parameter values
    geneticParameters = generate_Initial_Parameters(xData, yData)
    # curve fit and results
    popt, pcov = curve_fit(func, xData, yData, p0=geneticParameters, maxfev=1000)
    a,b,k = popt
    #results
    modelPredictions = func(xData, *popt) 
    absError = modelPredictions - yData 
    #df for plotting results in dash
    df_line = pd.DataFrame({
        "line_x": np.linspace(df[column1].min(),df[column1].max(), num=1000),
        "line_y": func(np.linspace(df[column1].min(),df[column1].max(), num=1000),*popt)
    })

    SE = np.square(absError) # squared errors
    MSE = np.mean(SE) # mean squared errors
    RMSE = np.sqrt(MSE) # Root Mean Squared Error, RMSE
    Rsquared = 1.0 - (np.var(absError) / np.var(yData))

    #table of contents
    df_results = pd.DataFrame({
                "Coeficientes e Erros":["a","b","k","RMSE","Rsquared"],
                "Valores":[round(a,4),round(b,4),round(k,4),round(RMSE,4),round(Rsquared,4)]
                }) 
    
    return df_results, df_line