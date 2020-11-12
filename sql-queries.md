##SQL Queries / Things to refer to

####Inner Joins

Selects records that have matching values in both tables

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

####Self Joins

Joins a table with itself

```
SELECT * FROM <table_name> a
JOIN <table_name> b
ON a.<column1_name> = b.<column2_name>
```

####Joining Multiple Tables

```
SELECT * FROM <table1_name> a
JOIN <table2_name> b
    ON a.<c1_name> = b.<c2_name>
JOIN <table3_name> c
    ON a(or b).<c3_name> = c.<c4_name>
```
