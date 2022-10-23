import siqueira_model
import regression_models
from pandas import DataFrame

def fit_to_model(df, x_column, y_column, model):
    # Default except return
    df_except_line = DataFrame({'line_x':[], 'line_y':[]})
    df_except_results = DataFrame({
            "Coeficientes e Erros":["Ocorreu um erro"],
            "Valores":["Não foi possível ajustar"]
            })
    
    if model == "E(t) = at +b(1-exp(-kt))": 
        try:
            return siqueira_model.siqueira_fit(df, x_column, y_column,)
        except:
            return df_except_results, df_except_line

    elif model == "Y(x) = ax + b":
        try:
            return regression_models.reg_lin(df, x_column, y_column,)
        except:
            return df_except_results, df_except_line
    
    elif model == "Y(x) = ax² + bx + c":
        try:
            return regression_models.polynomial2(df, x_column, y_column,)
        except:
            return df_except_results, df_except_line

    elif model == "Y(x) = b.exp(ax)":
        try:
            return regression_models.reg_exp(df, x_column, y_column,)
        except:
            return df_except_results, df_except_line
    elif model == "Y(x) = bxª":
        try:
            return regression_models.reg_power(df, x_column, y_column,)
        except:
            return df_except_results, df_except_line