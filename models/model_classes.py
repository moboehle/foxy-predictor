# This file contains all model classes

 # TODO: Dirty hack to import from sibling dir. Put wahlrecht_polling_firms.py into the same folder as this file eventually.
import sys
import os
sys.path.append(os.path.abspath('../Backend'))

import numpy as np
import pandas as pd
from model_helper import _prediction_to_dataframe
from model_helper import _normalize_to_hundred
from model_helper import parties
import preprocessing

import wahlrecht_polling_firms

#data_dict = wahlrecht_polling_firms.get_tables()
#data = preprocessing.average(data_dict, 'simple')

class Model():

    def fit(self, df=data):
        """Optional fit step to call before predictions. Leave empty if the model does not support fitting."""
        return

    def predict(self, df=data):
        raise NotImplementedError()

    def predict_all(self, df=data):
        """Make a prediction for each time point in the data."""
        #print('Applying model to {} time points...'.format(len(data)))

        # First prediction, append the other ones below.
        prediction_df = self.predict(df)

        for i in range(1, len(df)):
            # Note: Appending the data frames takes up almost no time here, the bottleneck is the model.
            prediction_df = prediction_df.append(self.predict(df[i:]), ignore_index=True)

        return prediction_df

    # TODO: With the new averaging in preprocessing, scoring the model against different polling firms isn't that simple any more. Maybe make a function in preprocessing that converts the data of a single polling firm to the weekly format.
    def score(self, data=data, polling_firm=None):
        """Calculate a score for the model (lower is better). The score is the mean squared error between the model's predictions and the true results.
        If `polling_firm` is None (default), return a dict with the score for each polling firm. Otherwise, return only the score for that polling firm."""
        prediction_df = self.predict_all(data)
        return mse(data, prediction_df)

        #if polling_firm is None:
        #    return {polling_firm: mse(poll_df, prediction_df) for polling_firm, poll_df in data_dict.items()}
        #else:
        #    return mse(data_dict[polling_firm], prediction_df)


# In[97]:

class PolynomialModel(Model):
    """Fit a polynomial of degree `degree` through the last `n_last` polls and calculate one point into the future."""

    def __init__(self, n_last=5, degree=1):
        self.n_last = n_last
        self.degree = degree

    def predict(self, df=data):
        # TODO: Double-check that this works properly.
        prediction = []

        if self.n_last == None:  # use all rows
            num_rows = len(df)
        else:  # use just the n_last rows
            num_rows = self.n_last

        data_for_regression = df[parties].iloc[:num_rows].fillna(0)
        x_pred = data_for_regression.index.values[0] - 1

        # TODO: Use dropna here.
        # Drop rows that contain only NaN values.
        data_for_regression = data_for_regression[[not (row == 0).all() for _, row in data_for_regression.iterrows()]]

        x = data_for_regression.index.values

        for party in parties:
            y = data_for_regression[party]

            if len(x) > 0 and len(y) > 0:
                y_pred = np.poly1d(np.polyfit(x, y, self.degree))(x_pred)
            else:
                y_pred = np.nan

            prediction.append(y_pred)

        prediction = _normalize_to_hundred(prediction)

        prediction_df = pd.DataFrame(columns=parties, index=[0])
        for i, party in enumerate(parties):
            mean = prediction[i]
            # TODO: Calculate error via scipy function and insert min/mean/max in here.
            prediction_df[party][0] = [mean, mean, mean]
        return prediction_df

# In[98]:

class LinearModel(PolynomialModel):
    """Fit a line through the last `n_last` polls and calculate one point into the future."""

    def __init__(self, n_last=5):
        PolynomialModel.__init__(self, n_last=n_last, degree=1)


# In[89]:

class DecayModel(Model):
    """Average the last `n_last` polls (`None`, i.e. all by default), where polls further back are weighted less (exponential decay)."""

    def __init__(self, n_last=None, decay_factor=0.9):
        self.n_last = n_last
        self.decay_factor = decay_factor

    def fit(self):
        # TODO: Fit decay_factor to get best results.
        pass

    # TODO: Maybe generalize by letting AverageModel and DecayModel inherit from each other or common base class.
    def predict(self, df=data):
        prediction = np.zeros(len(parties))
        prediction_error = np.zeros(len(parties))

        if self.n_last == None:  # use all rows
            num_rows = len(df)
        else:  # use just the n_last rows
            num_rows = self.n_last

        # TODO: Take decaying average of uncertainties according to p * (1-p) / n.

        for i in range(min(num_rows, len(df))):  # do not use more rows than the dataframe has
            results = df[parties].iloc[i].fillna(0)
            if not (results == 0).all():  # ignore empty rows
                prediction += results * self.decay_factor**(i+1)

                # Calculate error according to formula from paper: sqrt(p * (1-p) / n)
                p = results / 100
                n = df['Befragte'].fillna(0).iloc[i]
                if n > 0:
                    errors = 100 * np.sqrt(p * (1 - p) / n)
                    prediction_error += errors * self.decay_factor**(i+1)

        prediction = _normalize_to_hundred(prediction)

        prediction_df = pd.DataFrame(index=[0], columns=parties)
        for i, party in enumerate(parties):
            mean = prediction[i]
            error = prediction_error[i]
            prediction_df[party][0] = [mean - error, mean, mean + error]

        return prediction_df


# In[90]:

class AverageModel(DecayModel):
    """Average the last `n_last` polls (5 by default)."""

    def __init__(self, n_last=5):
        DecayModel.__init__(self, n_last=n_last, decay_factor=1)

# In[92]:

class LatestModel(AverageModel):
    """Use the latest poll."""

    def __init__(self):
        AverageModel.__init__(self, n_last=1)

# In[105]:

import GPflow

class GPModel(Model):
    """TODO. In contrast to the other models, GPModel always makes predictions for all time points. Therefore, `predict` just returns the latest data point from `predict_all`."""

    def __init__(self, k=GPflow.kernels.Matern32(1, variance=1, lengthscales=1.2)):
        self.kernel=k

    def predict(self, df=data):
        return self.predict_all(df).iloc[0]

    def predict_all(self, df=data):
        Y = df[parties]
        Y = Y.dropna(how='all').fillna(0)
        X = Y.index.values

        #X = pd.to_datetime(data.Datum)
        #X=-(X-dt.date.today()).astype('timedelta64[D]').reshape(-1,1)
        X = -X.reshape(-1,1).astype(float)

        #print(Y)

        m = GPflow.gpr.GPR(X, pd.DataFrame.as_matrix(Y), kern=self.kernel)
        m.optimize()

        x_pred = np.linspace(X[0,0],X[-1,0], 1000).reshape(-1,1)

        mean, var = m.predict_y(x_pred)
        # TODO: Integrate this into _normalize_to_hundred.
        prediction = 100 * mean / np.sum(mean, axis=1).reshape(-1, 1)

        prediction_df = pd.DataFrame(index=range(len(prediction)), columns=parties)
        for j in range(len(prediction)):
            for i, party in enumerate(parties):
                mean = prediction[j, i]
                prediction_df[party][j] = [mean, mean, mean]

        return prediction_df
