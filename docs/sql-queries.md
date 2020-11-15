## SQL Queries / Things to refer to

### Inner Joins

Selects records that have matching values in both tables.

```
SELECT * FROM <table1_name>
(INNER) JOIN <table2_name>
ON <table1_name>.<column_name> = <table2_name>.<column_name>
```

Alternately,

```
SELECT * FROM <table1_name>, <table2_name>
WHERE <table1_name>.<column_name> = <table2_name>.<column_name>
```

(This is called an implicit Join)

### Self Joins

Joins a table with itself.

```
SELECT * FROM <table_name> a
JOIN <table_name> b
ON a.<column1_name> = b.<column2_name>
```

### Joining Multiple Tables

```
SELECT * FROM <table1_name> a
JOIN <table2_name> b
    ON a.<c1_name> = b.<c2_name>
JOIN <table3_name> c
    ON a(or b).<c3_name> = c.<c4_name>
```

### Outer Joins

[A really goood diagram to understand this.](https://www.google.com/url?sa=i&url=https%3A%2F%2Fjavarevisited.blogspot.com%2F2013%2F05%2Fdifference-between-left-and-right-outer-join-sql-mysql.html&psig=AOvVaw098DpcRWZL3bN-EJnTbdHS&ust=1605337945108000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCOiwlIL8_uwCFQAAAAAdAAAAABAJ)

```
SELECT * FROM <table1_name>
LEFT JOIN <table2_name>
ON <table1_name>.<c1_name> = <table2_name>.<c2_name>
```

`LEFT` keyword shows all the records (even the ones that do not satisfy the `ON` condition) of the table named first.

### Outer Joins between multiple tables

Similar to 'Joining Multiple Tables'.

```
...
FROM <t1_name>
LEFT JOIN <t2_name>
ON ...
(LEFT, depends on the desired output) JOIN <t2_name>
ON ...
```

### Self Outer Joins

```
SELECT *
FROM <t1_name> a
LEFT JOIN <t1_name> b
ON a.<c1_name> = b.<c1_name>
```

### The USING clause

Used if the names of the columns are the same in both the tables.

```
SELECT * FROM <t1_name>
JOIN <t2_name>
    USING <c_name>

LEFT JOIN <t3_name>
    USING <c_name>

```

#### Composite Primary Key

A set of columns that, taken together, uniquely identify any record in a table.

```
...
USING (<PK_1>, <PK_2>)
...
```

### Natural Joins

Joins 2 tables automatically on the basis of columns having the same name.

```
SELECT * FROM <t1_name>
NATURAL JOIN <t2_name>
```

### Cross Joins

Cross product.

```
SELECT * FROM <t1_name>
CROSS JOIN <t2_name>
```

Alternately,

```
SELECT * FROM <t1_name>, <t2_name>
```

### Unions

Used to combine rows from different tables having the same columns and column types.

```
SELECT <c1_name>, <c2_name>, 'Active' AS status
FROM <t1_name>
WHERE (some_condition)

UNION

SELECT <c1_name>, <c2_name>, 'Archived' AS status
FROM <t1_name>
WHERE (some_condition)
```
