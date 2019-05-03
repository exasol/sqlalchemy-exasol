# parent image
FROM sqla:sqla

WORKDIR /sqla_exasol
ADD . /sqla_exasol

RUN pip install -e /sqla_exasol

CMD ["py.test", "--dropfirst", "--dburi exa+pyodbc://sqlalchemy_test:Th4nk_Y0u_4-SQLalchemY@213.95.157.51..57:8563/TEST_SCHEMA?CONNECTIONLCALL=en_US.UTF-8&DRIVER=EXAODBC"]
