# Issue - Prepared Statement With Cast of Parameter

## Scenario

Assuming that the user wants to execute the following prepared statement:

```sql
INSERT INTO t (x) VALUES (CAST(? AS VARCHAR(50))); 
```

### Questions
* Is this a legit prepared statement?
  - Server seems to accept the SQL
  - What are the constraints and assumptions for such a prepared statement if allowed?
* Who is responsible for validating the data types in such a scenario? (client, server)
  - Without "full" semantic understanding how could a client validate this?


### JDBC via Datagrip

Works fine but Datagrip is replacing the `?` before sending the statment.
(It does do an insert not an prepared insert)

```sql
-- Prepare test
DROP SCHEMA IF EXISTS TEST CASCADE;
CREATE SCHEMA TEST;
CREATE TABLE TEST.T(x VARCHAR(50));

-- Execute Test
INSERT INTO TEST.T (x) VALUES (CAST(? AS VARCHAR(50))); -- params tested: 1, '1', 1.0, 1.1

-- Check Table
SELECT * FROM TEST.T;
```

### WSS via SQLA 

#### Summary
The server accepts the prepared statement, but informs the client that the expect type for the
data is VARCHAR, as the client passes the original data (ints) the server fails when it is
requested to execute the prepared statement with the given data.

#### Notes

* 127.0.0.1:8888  Database
* 127.0.0.1:57568 Client

#### Communication

```json
...

127.0.0.1:57568 -> 127.0.0.1:8888
{"command": "execute", "sqlText": "CREATE TABLE t (\n\tx VARCHAR(50)\n)"}

127.0.0.1:8888 -> 127.0.0.1:57568
{"status":"ok","responseData":{"results":[{"resultType":"rowCount","rowCount":0}],"numResults":1}}

127.0.0.1:57568 -> 127.0.0.1:8888
{"command": "createPreparedStatement", "sqlText": "INSERT INTO t (x) VALUES (CAST(? AS VARCHAR(50)))"}

127.0.0.1:8888 -> 127.0.0.1:57568
{"status":"ok","responseData":{"statementHandle":7,"parameterData":{"numColumns":1,"columns":[{"name":"","dataType":{"type":"VARCHAR","size":2000000,"characterSet":"UTF8"}}]},"results":[{"resultType":"rowCount","rowCount":0}],

127.0.0.1:57568 -> 127.0.0.1:8888
{"command": "executePreparedStatement", "statementHandle": 7, "numColumns": 1, "numRows": 3, "columns": [{"name": "", "dataType": {"type": "VARCHAR", "size": 2000000, "characterSet": "UTF8"}}], "data": [[1, 2, 3]]}

127.0.0.1:8888 -> 127.0.0.1:57568
{"status":"error","exception":{"text":"getString: JSON value is not a string. (Session: 1765399198642536448)","sqlCode":"00000"}}

127.0.0.1:57568 -> 127.0.0.1:8888
{"command": "closePreparedStatement", "statementHandle": 7}

127.0.0.1:8888 -> 127.0.0.1:57568
{"status":"ok"}

...
```

### WSS via pyexasol

```python
TBD
```

### odbc via pyodbc

```python
TBD
```

