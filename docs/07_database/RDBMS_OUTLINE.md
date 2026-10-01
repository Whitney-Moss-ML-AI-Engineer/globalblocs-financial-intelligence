# GlobalBLOCS Relational Database Management System (RDBMS) Outline

## I–IX. Foundations and relational design
1. RDBMS definition, history, E. F. Codd, purpose, file-system advantages.
2. Data, information, metadata; database; DBMS; RDBMS versus DBMS.
3. Relations, tuples, attributes, domains, cardinality, degree; primary, candidate, alternate, composite, surrogate, natural, foreign, and super keys.
4. Database/schema/table/column/record/view/index/sequence/materialized view/partition/cluster.
5. Numeric, character, date/time, Boolean, binary, JSON/XML types.
6. 1:1, 1:N, M:N, and self-referencing relationships.
7. ER entities, attributes, relationships, cardinality, participation, weak/strong entities, diagrams.
8. Conceptual → logical → physical database design.
9. 1NF, 2NF, 3NF, BCNF, 4NF, 5NF, and deliberate denormalization.

## X–XV. SQL and data access
10. DDL, DML, DQL, DCL, TCL.
11. WHERE, ORDER BY, GROUP BY, HAVING, DISTINCT, LIMIT/OFFSET, CASE, COALESCE, NULLIF.
12. INNER, LEFT, RIGHT, FULL, CROSS, SELF joins.
13. Aggregate, string, date/time, mathematical, and window functions.
14. PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK, DEFAULT, NOT NULL.
15. Clustered/non-clustered concepts, composite, bitmap, covering, hash, full-text indexing; document vendor-specific support.

## XVI–XXII. Enterprise database engineering
16. ACID, isolation levels, locking, deadlocks, MVCC, optimistic/pessimistic concurrency.
17. Standard, materialized, and updatable views.
18. Procedures, functions, triggers, packages where supported, and events.
19. Authentication, authorization, roles, privileges, encryption, auditing, row-level security.
20. Full/differential/incremental backup, point-in-time recovery, log shipping, replication, disaster recovery.
21. Query optimization, execution plans, statistics, index tuning, partitioning, sharding, caching, connection pooling.
22. Replication, failover, clustering, load balancing, distributed databases.

## XXIII–XXVIII. Platforms, architecture, applications, analytics
23. Oracle, SQL Server, Db2, PostgreSQL, MySQL, MariaDB, SQLite, Amazon Aurora.
24. Client → API/application → parser → optimizer → execution engine → storage/cache → WAL/transaction log → durable storage.
25. Banking, healthcare, government, retail, manufacturing, telecom, supply chain, HR, education, e-commerce, financial analytics, BI, warehousing.
26. Star/snowflake schemas, facts/dimensions, OLTP/OLAP, ETL/ELT.
27. SQL analytics, Python DB APIs, JDBC, ODBC, ORM, ML pipelines, data lakes/warehouses, feature stores, RAG.
28. SQL, data modeling, performance tuning, backup/recovery, security, DBA, data engineering, BI, cloud databases, Python DB programming, ETL, governance.

## GlobalBLOCS implementation standard

PostgreSQL is the reference RDBMS. The normalized core stores source/dataset metadata, entities, institutions, instruments, periods, observations, lineage, and quality results. Star-schema/materialized-view layers serve dashboard analytics. Raw API payloads and large extracts remain immutable in object storage/Parquet.
