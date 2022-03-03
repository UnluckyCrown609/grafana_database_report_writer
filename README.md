# grafana_database_report_writer

## Installation

### Data Sources

- Postgres

![](readme_files/postgres_datasource.jpg){width = 400px}

- Influxdb

![](readme_files/influxdb_datasource.jpg){width = 400px}
      
## PostgresSQL-Timescale Configuration

### Table SQL Query

To create a timescaledb hypertable use this sql:
```
CREATE TABLE IF NOT EXISTS public.testing_1
(
    "time" timestamp without time zone NOT NULL,
    volt double precision,
    ampere double precision,
    watt double precision
);

SELECT create_hypertable('testing_1','time');
```
```
CREATE TABLE IF NOT EXISTS public.testing_2
(
    "time" timestamp without time zone NOT NULL,
    device text COLLATE pg_catalog."default",
    host text COLLATE pg_catalog."default",
    metric text COLLATE pg_catalog."default",
    unit text COLLATE pg_catalog."default",
    value double precision
);

SELECT create_hypertable('testing_2','time');
```
### Python Insertion Example

- table testing_1 is a long table format
- table testing_2 is a short table format

```
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
```

### Telegraf Insertion Config

```
# Output to TimescaleDB, including creating hypertable
[[outputs.sql]]

driver = "pgx"

data_source_name = "postgres://lab:Password01@timescaledb:5432/lab"
timestamp_column = "time"
table_template = "CREATE TABLE {TABLE}({COLUMNS}); SELECT create_hypertable('{TABLE}','time')"

[outputs.sql.convert]
integer = "double precision"
real = "double precision"
text = "text"
timestamp = "TIMESTAMP"
defaultvalue = "text"
unsigned = ""
```

### Grafana 

Need to create a variable in the dashboard settings:
```
SELECT CONCAT('avg(NULLIF(', column_name, ',$$NaN$$)) AS ', column_name) AS column FROM information_schema.columns WHERE table_name='testing_2' AND column_name SIMILAR TO '%volt'
```
Then add this query into the dashboard panel (in this example volt, ampere & watt are the variable names related to above):
```
SELECT $__timeGroup(time,$__interval) AS "time",
  ${volt:csv},
  ${ampere:csv},
  ${watt:csv}
FROM
  lab.public.testing_2
WHERE
  $__timeFilter(time)
GROUP BY time
ORDER BY time
```