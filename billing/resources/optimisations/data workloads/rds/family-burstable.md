    - Check your t family usage as they are a burstable instance  
      - Review your CPU Utilisation and Burstable Credit metrics to check you are using them efficiently  
      - Baseline CPU is calculated according to instance and size[^b1]  
        - Above baseline uses credits until they run out after which you are charged  
        - Below baseline earns credits  

[^b1]:  https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/burstable-credits-baseline-concepts.html\#earning-CPU-credits