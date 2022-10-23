from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import numpy as np
import pandas as pd

def reg_lin(df, x_column, y_column):
    xData, yData = df[x_column].values.reshape(-1,1), df[y_column].values.reshape(-1,1)
    model = LinearRegression().fit(xData, yData)
    #results
    modelPredictions = model.predict(xData) 
    absError = modelPredictions - yData 

    SE = np.square(absError) # squared errors
    MSE = np.mean(SE) # mean squared errors
    RMSE = np.sqrt(MSE) # Root Mean Squared Error, RMSE
    Rsquared = 1.0 - (np.var(absError) / np.var(yData))

    #df for plotting results in dash
    line_x = np.linspace(df[x_column].min(),df[x_column].max(), num=1000)
    line_y = model.predict(line_x.reshape(-1,1))
    df_line = pd.DataFrame({
        "line_x": line_x,
        "line_y": line_y.reshape(1,-1)[0]
    })
    
    #table of contents
    df_results = pd.DataFrame({
                "Coeficientes e Erros":["a","b","RMSE","Rsquared"],
                "Valores":[round(model.coef_[0][0],4),round(model.intercept_[0],4),round(RMSE,4),round(Rsquared,4)]
                }) 

    return df_results, df_line

def reg_exp(df, x_column, y_column):
    xData, yData = df[x_column].values.reshape(-1,1), df[y_column].apply(lambda x:np.log(x)).values.reshape(-1,1)
    model = LinearRegression().fit(xData, yData)
    #results
    modelPredictions = model.predict(xData) 
    absError = modelPredictions - yData 

    SE = np.square(absError) # squared errors
    MSE = np.mean(SE) # mean squared errors
    RMSE = np.sqrt(MSE) # Root Mean Squared Error, RMSE
    Rsquared = 1.0 - (np.var(absError) / np.var(yData))

    #df for plotting results in dash
    line_x = np.linspace(df[x_column].min(),df[x_column].max(), num=1000)
    line_y = model.predict(line_x.reshape(-1,1))
    df_line = pd.DataFrame({
        "line_x": line_x,
        "line_y": line_y.reshape(1,-1)[0]
    })
    df_line['line_y'] = df_line['line_y'].apply(lambda y: np.exp(y))
    
    #table of contents
    df_results = pd.DataFrame({
                "Coeficientes e Erros":["a","b","RMSE","Rsquared"],
                "Valores":[round(model.coef_[0][0], 4),round( np.exp(model.intercept_[0]), 4 ),round(RMSE,4),round(Rsquared,4)]
                }) 

    return df_results, df_line

def reg_power(df, x_column, y_column):
    xData, yData = df[x_column].apply(lambda x:np.log(x)).values.reshape(-1,1), df[y_column].apply(lambda x:np.log(x)).values.reshape(-1,1)
    model = LinearRegression().fit(xData, yData)
    #results
    modelPredictions = model.predict(xData) 
    absError = modelPredictions - yData 

    SE = np.square(absError) # squared errors
    MSE = np.mean(SE) # mean squared errors
    RMSE = np.sqrt(MSE) # Root Mean Squared Error, RMSE
    Rsquared = 1.0 - (np.var(absError) / np.var(yData))

    #df for plotting results in dash
    line_x = np.linspace( df[x_column].min(), df[x_column].max(), num=1000 )
    line_y = model.predict(np.log(line_x).reshape(-1,1))
    df_line = pd.DataFrame({
        "line_x": line_x,
        "line_y": line_y.reshape(1,-1)[0]
    })
    df_line['line_y'] = df_line['line_y'].apply(lambda y: np.exp(y))

    #table of contents
    df_results = pd.DataFrame({
                "Coeficientes e Erros":["a","b","RMSE","Rsquared"],
                "Valores":[round(model.coef_[0][0], 4),round( np.exp(model.intercept_[0]), 4 ),round(RMSE,4),round(Rsquared,4)]
                }) 

    return df_results, df_line

def polynomial2(df, x_column, y_column):
    xData, yData = df[x_column].values.reshape(-1,1), df[y_column].values.reshape(-1,1)
    poly_feature = PolynomialFeatures(degree = 2, include_bias = False)
    X_poly = poly_feature.fit_transform(xData)

    model = LinearRegression().fit(X_poly, yData)
    #results
    modelPredictions = model.predict(X_poly) 
    absError = modelPredictions - yData 

    SE = np.square(absError) # squared errors
    MSE = np.mean(SE) # mean squared errors
    RMSE = np.sqrt(MSE) # Root Mean Squared Error, RMSE
    Rsquared = 1.0 - (np.var(absError) / np.var(yData))

    #df for plotting results in dash
    line_x = np.linspace(df[x_column].min(),df[x_column].max(), num=1000)
    line_y = model.predict(poly_feature.fit_transform(line_x.reshape(-1,1)))
    df_line = pd.DataFrame({
        "line_x": line_x,
        "line_y": line_y.reshape(1,-1)[0]
    })
    
    #table of contents
    df_results = pd.DataFrame({
                "Coeficientes e Erros":["a","b","c","RMSE","Rsquared"],
                "Valores":[round(model.coef_[0][0],4),round(model.coef_[0][1],4),round(model.intercept_[0],4),round(RMSE,4),round(Rsquared,4)]
                }) 

    return df_results, df_line