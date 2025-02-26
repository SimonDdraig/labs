    - Check your t family usage as they are a burstable instance  
      - Review your CPU Utilisation and Burstable Credit metrics to check you are using them efficiently  
      - Baseline CPU is calculated according to instance and size[^b1]  
        - Above baseline uses credits until they run out after which you are charged  
        - Below baseline earns credits  
      - Throttling can occur on a burstable instance  
        - Check remaining credits on the CPU credit balance (see this metric on the monitoring tab of the instance)  
        - If the credit balance is close to zero, then the instance CPU is likely being throttled  
        - To resolve this issue, you can either turn on T2/T3 Unlimited or change the instance type  

[^b1]:  https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/burstable-credits-baseline-concepts.html\#earning-CPU-credits