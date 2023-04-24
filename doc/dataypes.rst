Python Datatype	Description	ODBC Datatype
None	null	varies (1)
bool	boolean	BIT
int	integer	SQL_BIGINT
float	floating point	SQL_DOUBLE
decimal.Decimal	decimal	SQL_NUMERIC
str	UTF-16LE (2)	SQL_VARCHAR or SQL_LONGVARCHAR (2)(3)
bytes, bytearray	binary	SQL_VARBINARY or SQL_LONGVARBINARY (3)
datetime.date	date	SQL_TYPE_DATE
datetime.time	time	SQL_TYPE_TIME
datetime.datetime	timestamp	SQL_TYPE_TIMESTAMP
uuid.UUID	UUID / GUID	SQL_GUID


.. list-table:: Data type mappings
   :widths: 34 33 33
   :header-rows: 1

   * - Python Datatype
     - EXASOL Datatype
     - Description
   * - None
     - NULL
     -
   * - bool
     - BOOLEAN
     -
   * - int
     - DECIMAL (scale = 0)
     -
   * - float
     - DOUBLE PRECISION
     -
   * - decimal.Decimal
     - DECIMAL(...)
     -
   * - str
     - CHAR / VARCHAR
     -
   * - bytes, bytearray
     - not supported
     -
   * - datetime.date
     -



Questions:
* Is the type Null a type? or a value or both?
*


See also: link