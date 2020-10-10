# Barcelona House Price Prediction

I wrote this application to learn how to develop a single-page app.
The app gives suggestion on the price one should pay for an apartment in select neighbourhoods of Barcelona, based on a dataset of offer prices.

## Backend

The backend is written in Python and uses FastAPI to serve requests.
Resource '/' expects five parameters:

* `neighbourhood` (string): either `'sarria'` or `'poblenou'`;
* `sqm` (int): square metres;
* `rooms` (int): number of bedrooms;
* `state` (str): either `'need_renovation'`, `'second_hand'` or `'new'`;
* `elevator` (boolean): whether the builing has an elevator.

If returns a JSON object with information on how much you should pay, a comparison with similar apartments, and an array of similar listings.

One can launch the server from the `backend` folder with command `uvicorn main --reload`.

## Frontend

The frontend is a React single-page app with a form to input the data.
It performs a `fetch` request to the backend and presents the resutls to the user.

## License

This software is released under the GPLv3 license (see file `LICENSE`).
