### Other Considerations

Applies to data services such as RDS, Aurora, OpenSearch, Redshift, ElastiCache, etc.

**RDS optimised reads** \- achieve [faster query processing](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-optimized-reads.html)[^f1] for RDS MySQL.

**RDS optimised writes** \- [improved performance](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-optimized-writes.html)[^f2] of write transactions for RDS MySQL.

**Multi-AZ** \- Use in production workloads only. Not typically used in non-production environments.

**Consolidate small databases** \- RDS can support running multiple databases on the same instance. Simplifies the management, and optimises the costs of staging and dev environments.

**Athena query reuse** \- When you re-run a query in Athena, you can optionally choose to reuse the [last stored query result](https://docs.aws.amazon.com/athena/latest/ug/reusing-query-results.html)[^f3]. This option can increase performance and reduce costs in terms of the number of bytes scanned.

**S3 scanning** \- Partition data lakes to ensure scanning is limited to subsets of data, from services such as Redshift Spectrum and Athena. 

**OpenSearch data tiering** \- Enables [optimisation of storage](https://aws.amazon.com/opensearch-service/features/#Storage_tiering)[^f4] and cost-efficiency of data while maintaining the ability to search and analyse it at similar performance to the Hot storage.

**Transfers** \- Review transfer of data between accounts, regions and to other destinations such as on premise. Egress out of AWS can be expensive.

[^f1]: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-optimized-reads.html  
[^f2]: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-optimized-writes.html  
[^f3]: https://docs.aws.amazon.com/athena/latest/ug/reusing-query-results.html  
[^f4]: https://aws.amazon.com/opensearch-service/features/#Storage_tiering  