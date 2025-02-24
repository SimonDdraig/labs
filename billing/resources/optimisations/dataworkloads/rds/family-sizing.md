    - Sizing  
      - If you are confident in the sizing of your instances, consider reserved instance pricing for considerable savings  
      - Consider key metrics of provisioned RDS[^s1]/Aurora[^s2] to see if the instance family and size are meeting the load demands[^s3]:  
        - CPU Utilisation  
        - Memory  
        - Disk Queue Depth  
        - IOPS  
        - Latency  
      - Check EBS and Network bandwidth utilization to make sure downgrading the instance size does not negatively impact throughput requirements  

[^s1]: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-metrics.html  
[^s2]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.AuroraMonitoring.Metrics.html
[^s3]: https://aws.amazon.com/blogs/database/making-better-decisions-about-amazon-rds-with-amazon-cloudwatch-metrics/  