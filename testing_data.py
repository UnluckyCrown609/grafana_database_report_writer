from random import randint
import pandas as pd
import time
from sqlalchemy import create_engine
from influx_line_protocol import Metric, MetricCollection


def log():
    db = 'postgresql+psycopg2://lab:Password01@192.168.0.19:5432/lab'
    volts = randint(0, 100)
    amperes = randint(0, 10)
    watts = volts * amperes

    table = 'testing_1'
    df = pd.DataFrame({'time': pd.Timestamp.now(),
                       'volt': [volts],
                       'ampere': [amperes],
                       'watt': [watts]}, index=[0])
    with create_engine(db).connect() as con:
        df.to_sql(table, con, if_exists='append', index=False)
    print(df)

    table = 'testing_2'
    p = {'volt': volts, 'amp': amperes, 'watt': watts}
    device = 'power_supply_sim'
    host = 'my_computer'
    times = pd.Timestamp.now()
    for x, y in zip(p.keys(), p.values()):
        df = pd.DataFrame({'time': [times],
                           'device': [device],
                           'host': [host],
                           'metric': [f'metric_name_{x}'],
                           'unit': [x],
                           'value': [y]},
                          index=[0])
        print(df)
        with create_engine(db).connect() as con:
            df.to_sql(table, con, if_exists='append', index=False)


if __name__ == "__main__":

    while True:
        time.sleep(10)

        log()
