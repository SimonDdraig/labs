    - Upgrade your gp2 volumes  
      - Check your storage configuration, you have older gp2 volumes and could upgrade to gp3[^g1]:  
        - Up to 20% lower price per GB than existing gp2 volumes  
        - Larger selection of storage capacity  
        - Baseline storage performance of 3,000 IOPS included with the price of storage  
          - Larger storage can increase IOPS, eg 400 GiB gets 12,000 IOPS  
          - But consider instance class and size, as they can be capped at a lower IOPS value  
        - For workloads that need even more performance, you can scale up to 64,000 IOPS for an additional cost  
          - Larger IOPS requirements should consider io2 storage volumes rather than gp3  

[^g1]:  https://aws.amazon.com/ebs/general-purpose/