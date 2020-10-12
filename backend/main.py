import pandas as pd
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000', 'https://localhost:3000'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
def get(neighbourhood: str, sqm: int, rooms: int, state: str, elevator: bool):
    data = get_data(neighbourhood)
    model = get_model(data, sqm, rooms)
    result = get_result(data, model, sqm, rooms, state, elevator)

    return result


def get_data(neighbourhood: str):
    df = pd.read_csv(f"data/{neighbourhood}.csv")
    return df[(df.sqm > 0) & (df.rooms > 0) & (df.price > 0)]


def get_model(data: pd.DataFrame, sqm: int, rooms: int):
    d = data[(data.sqm != sqm) & (data.rooms != rooms)]
    X = d[['sqm', 'rooms', 'state', 'elevator']]
    y = d[['price']]

    numeric_features = ['sqm', 'rooms']
    categorical_features = ['state', 'elevator']

    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())])
    categorical_transformer = Pipeline(steps=[
        ('encoder', OneHotEncoder(handle_unknown='error', drop='first'))])
    preprocessor = ColumnTransformer(transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)])

    model = Pipeline(steps=[
        ('preprocess', preprocessor),
        ('linreg', LinearRegression())])

    model.fit(X, y)

    training_preds = model.predict(X).flatten()
    real_labels = y.values.flatten()
    stddev = np.sqrt(sum((training_preds - real_labels) ** 2) / (len(y) - 2))

    return dict(pipeline=model, stddev=stddev)


def get_prediction(model: dict, sqm: int, rooms: int, state: str, elevator: bool):
    pred = model['pipeline'].predict(pd.DataFrame(dict(
        sqm=[sqm], rooms=[rooms], state=[state], elevator=[elevator])))
    pred = pred.flatten()[0] * .95

    return dict(
        cost=roundk(pred),
        lower_bound=roundk(pred - 0.25 * model['stddev']),
        upper_bound=roundk(pred + 0.25 * model['stddev'])
    )


def get_comparative(data: pd.DataFrame, sqm: int, rooms: int, state: str, elevator: bool):
    comparative = dict()

    d = data[(data.sqm >= .95 * sqm) & (data.sqm <= 1.05 * sqm) & (data.elevator == elevator)]
    if len(d) > 0:
        p = d.price.mean()
        comparative['by_sqm'] = roundk(p * .95)

    d = data[(data.rooms == rooms) & (data.elevator == elevator)]
    if len(d) > 0:
        p = d.price.mean()
        comparative['by_rooms'] = roundk(p * .95)

    d = data[(data.state == state) & (data.elevator == elevator)]
    if len(d) > 0:
        p = d.price.mean()
        comparative['by_state'] = roundk(p * .95)

    return comparative


def get_similar(data: pd.DataFrame, sqm: int, rooms: int, state: str, elevator: bool):
    d = data[(data.sqm >= sqm * .75) & (data.sqm <= sqm * 1.25)]
    d = d[(d.rooms >= rooms - 1) & (d.rooms <= rooms + 1)]

    if len(d) > 10:
        d = d[d.state == state]
        if len(d) > 10:
            d = d[d.elevator == elevator]

    return d.to_dict('records')


def get_result(data: pd.DataFrame, model: dict, sqm: int, rooms: int, state: str, elevator: bool):
    prediction = get_prediction(model, sqm, rooms, state, elevator)
    comparative = get_comparative(data, sqm, rooms, state, elevator)
    similar = get_similar(data, sqm, rooms, state, elevator)

    return dict(prediction=prediction,
                comparative=comparative,
                similar=similar)


def roundk(x):
    return 1000 * round(x/1000)
