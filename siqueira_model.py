import numpy as np
import pandas as pd
from scipy.optimize import curve_fit, differential_evolution
import warnings

def siqueira(t, a, b, k):
    return a*t + b*(1 - np.exp(-k*t))

# function for genetic algorithm to minimize (sum of squared error)
def sumOfSquaredError(parameterTuple, *args):
    xData, yData = args
    warnings.filterwarnings('ignore')
    val = siqueira(xData, *parameterTuple)
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

def siqueira_fit(df, x_column, y_column):
    xData, yData = df[x_column], df[y_column]

    # generate initial parameter values
    geneticParameters = generate_Initial_Parameters(xData, yData)
    
    # curve fit and results
    popt, pcov = curve_fit(siqueira, xData, yData, p0=geneticParameters, maxfev=1000)
    
    #results
    modelPredictions = siqueira(xData, *popt) 
    absError = modelPredictions - yData 

    SE = np.square(absError) # squared errors
    MSE = np.mean(SE) # mean squared errors
    RMSE = np.sqrt(MSE) # Root Mean Squared Error, RMSE
    Rsquared = 1.0 - (np.var(absError) / np.var(yData))

    #df for plotting results in dash
    df_line = pd.DataFrame({
        "line_x": np.linspace(df[x_column].min(),df[x_column].max(), num=1000),
        "line_y": siqueira(np.linspace(df[x_column].min(),df[x_column].max(), num=1000),*popt)
    })
    
    #table of contents
    df_results = pd.DataFrame({
                "Coeficientes e Erros":["a","b","k","RMSE","Rsquared"],
                "Valores":[round(popt[0],4),round(popt[1],4),round(popt[2],4),round(RMSE,4),round(Rsquared,4)]
                }) 
                
    df_line = pd.DataFrame({'line_x':[], 'line_y':[]})
    df_results = pd.DataFrame({
        "Coeficientes e Erros":["Ocorreu um erro"],
        "Valores":["Não foi possível ajustar"]
        }) 

    return df_results, df_line