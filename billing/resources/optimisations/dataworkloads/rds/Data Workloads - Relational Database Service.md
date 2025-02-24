  - Network Provisioning  
    - Consider your Provisioned (baseline) IOPS and compare with the TotalIOPS metric, check if it is within the 90% threshold  
    - Consider the sum of ReadThroughput and WriteThroughput, compare with your Storage throughput to see how much is within limits  
    - PIOPS (provisioned io1/io2)  
      - m4.large can only handle maximum of 3,600 IOPS  
      - If PIOPS is greater than 12,000, then check to see if gp3 or gp2 with the same IOPS is cheaper  
      -   
  - RDS Scaling  
    - Horizontal scaling vs vertical scaling  
      - If your instance is undersized, and you consider vertical scaling as a solution, horizontal might be cheaper  
      - Vertical scaling can be twice as much when you upsize; eg xlarge to 2xlarge  
      - Horizontal scaling can be cheaper if it allows you to scale horizontally to a smaller instance for the replica; eg, your primary remains an xlarge, your replica is sized as a large  
    - Using a distributed cache such as Elasticache can decrease costs  
      - If you have resultsets that are commonly served, caching them can offload the requests to a distributed cache rather than scaling your instance  
      - Applicable to scenarios where you don't have many dynamic, unique, or ad hoc generates requests  
  - Licensing  
    - Consider migrating away from RDS SQL Server to MySQL or Postgres  
      - Beat those Microsoft licensing costs  
  - Aurora I/O Optimised  
    - Consider Aurora I/O Optimised[^5] mode for clusters where I/O costs account for more than 25% of the overall cluster expenses:  
      - This change can provide substantial cost savings while potentially enhancing performance  
      - Aurora I/O Optimised offers a predictable pricing structure compared to the pay-as-you-go style of the Standard mode for I/O usage  
      - This transition may also lead to performance improvements as a valuable additional benefit  
      - Aurora I/O Optimised mode is designed to efficiently handle workloads with intensive I/O requirements, making it well-suited for scenarios where I/O costs are a significant portion of your cluster expenses  
    - For example (NOT based on your invoice, N. Virginia US$ pricing used in this example for on demand)  
      - Instance cost  
        R6g.xlarge \= 30 days \* 24 hrs \* **$0.519** \= **$373.68**  
      - Storage cost with growth of 100 MB per day  
        (100 GB \* 30 days \+ 100 MB \* 30 days \+ 100 MB \* 28 days etc) \* **$0.10** per GB \= **$300.15**  
      - Regular I/Os per Month (up to 600 I/Os)  
        600 \* 30 days \* 24 hrs \* 60 mins \* 60 seconds \* **$0.20** per million \= **$311.04**  
      - But lets say you experience a bursty IO for a couple of hours per day  
        15000 \* 30 days \* 2 hrs \* 60 mins \* 60 seconds \* **$0.20** per million \= **$648.00** (additional cost)  
      - **Total Cost \= $1632.87**  
    - Options for this scenario  
      - Increase the size of the instance  
        - Bigger cache which improves cache hit rate  
        - Less IO  
        - Can reduce I/O cost  
        - Doesn't necessarily insulate against burstable traffic  
        - Not predictable cost  
      - Aurora I/O Optimised  
        - Pay larger amount for storage  
        - Pay no cost for I/O  
        - Get price predictability  
        - Up to 40% savings if your I/O costs exceeded your storage cost by approximately 25%  
        - Also increases throughput and reduced I/O latency  
        - Switch it on and off with no impact (once a month)  
        - Instance cost  
          R6g.xlarge \= 30 days \* 24 hrs \* **US$0.675** \= **$486**  
        - Storage cost with growth of 100 MB per day  
          (100 GB \* 30 days \+ 100 MB \* 30 days \+ 100 MB \* 28 days etc) \* **$0.225** per GB \= **$675.33**  
        - Regular I/Os per Month (up to 600 I/Os)  
          **$0.00**  
        - But lets say you experience a bursty IO for a couple of hours per day  
          **$0.00**  
        - **Total Cost \= $1161.33** (previously $1632.87)  
  - Aurora Cloning  
    - If you are replicating your production environments into non-production for development or testing, instead of taking the snapshot and paying for its storage, you can use Aurora Cloning[^6]  
    - It costs nothing in terms of storage until data is changed  
    - You can also share a clone for cross account cloning  
  - Aurora Serverless  
    - Consider your Aurora Serverless costs and the ACU's you have specified:  
      - Check the ACU Utilisation percentage to see how much ACU is being used  
      - Is a provisioned instance cheaper if you do not have unpredictable, inconsistent load  
      - It can now (as of Re-Invent 2024\) scale up to 256 ACU, and down to 0 ACU charging you nothing for compute if it does so  
  - Usage  
    - Stop any instances that are not being used:  
      - Consider non production loads/accounts too  
      - Use AWS Instance Scheduler[^7] to auto shut down instances when not required  
    - Do you need the same sized instances in non-production environments  
    - Do you need multi-az in non-production environments

[^1]:  https://aws.amazon.com/ebs/general-purpose/

[^2]:  https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/burstable-credits-baseline-concepts.html\#earning-CPU-credits

[^3]:  https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.AuroraMonitoring.Metrics.html

[^4]:  https://aws.amazon.com/blogs/database/making-better-decisions-about-amazon-rds-with-amazon-cloudwatch-metrics/

[^5]:  [https://aws.amazon.com/blogs/aws/new-amazon-aurora-i-o-optimized-cluster-configuration-with-up-to-40-cost-savings-for-i-o-intensive-applications/](https://aws.amazon.com/blogs/aws/new-amazon-aurora-i-o-optimized-cluster-configuration-with-up-to-40-cost-savings-for-i-o-intensive-applications/) 

[^6]:  https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Managing.Clone.html

[^7]:  https://aws.amazon.com/solutions/implementations/instance-scheduler-on-aws/