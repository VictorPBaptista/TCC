import siqueira_model
import regression_models

def fit_to_model(df, x_column, y_column, model):
    if model == "E(t) = at +b(1-exp(-kt))": 
        return siqueira_model.siqueira_fit(df, x_column, y_column,)
    elif model == "Y(x) = ax + b":
        return regression_models.reg_lin(df, x_column, y_column,)
    elif model == "Y(x) = ax² + bx + c":
        return regression_models.polynomial2(df, x_column, y_column,)
    elif model == "Y(x) = b.exp(ax)":
        return regression_models.reg_exp(df, x_column, y_column,)
    elif model == "Y(x) = bxª":
        return regression_models.reg_power(df, x_column, y_column,)