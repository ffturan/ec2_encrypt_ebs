# ec2_encrypt_ebs
AWS EBS volume encryption.  
This is how it goes.  
  - Find aws/ebs encryption key for the account Id.  
  - Find all attached EBS volumes.  
  - Exclude root EBS volume.  
  - Check if EBS volume is already encrypted.  
  - Get EBS volume type, zone, IOPs values for future use.
  - Create snapshot from the EBS volume.  
  - Create a new encrypted snapshot from the previous snapshot.  
  - Create a new EBS volume from encrypted snapshot.  
  - Detach original EBS volume.  
  - Attach new encrypted EBS volume.  
  - Remove snapshot and encrypted snapshot created from original EBS volume.  
  - Don't touch original EBS volume.  
  - Move next EBS volume in the list.  

Works with gp2 and io1 EBS volumes.  

## Requirements
Be sure that target EC2 instance is in "stopped" state.  
Be sure that you have working backups of your EC2 instance.  
Requires AWS profile/region/instance-id as input.  

## 
## Usage
./ec2_encrypt_ebs profile-name region-name instance-id
## Sample Output
```shell
Following aws/ebs encryption key will be used:
arn:aws:kms:us-east-1:xxxxxxxxxxxx:alias/aws/ebs
Following volumes found:
['/dev/sdu', 'vol-xxxxxxxx', 'us-east-1d']
['/dev/sdd', 'vol-yyyyyyyy', 'us-east-1d']
['/dev/sdc', 'vol-zzzzzzzz', 'us-east-1d']
['/dev/sdr', 'vol-qqqqqqqq', 'us-east-1d']
['/dev/sds', 'vol-wwwwwwww', 'us-east-1d']
['/dev/sdt', 'vol-ffffffff', 'us-east-1d']
['/dev/sdf', 'vol-aaaaaaaa', 'us-east-1d']
['/dev/xvdab', 'vol-dddddddd', 'us-east-1d']
Working on Volume:vol-xxxxxxxx, Zone:us-east-1d, Type:io1, Iops:5000, Is Encrypted:False
New snapshot created: snap-0578aa472b555a0a5
++
Waiting for snap-0578aa472b555a0a5 to become available ...
++
New encrypted snapshot created: snap-071dfb65cfa72e317
++
Waiting for snap-071dfb65cfa72e317 to become available ...
++
New encrypted volume created: vol-00000000000000000
++
Waiting for vol-00000000000000000 to become available ...
++
Detaching orignal volume : vol-xxxxxxxx
Waiting for vol-xxxxxxxx to become detached ...
++
Attaching encrypted volume : vol-00000000000000000
++
Waiting for vol-00000000000000000 to become attached ...
++
New encrypted volume attached: vol-00000000000000000
++
Cleaning up snapshot : snap-0578aa472b555a0a5
Cleaning up snapshot : snap-071dfb65cfa72e317
Working on Volume:vol-yyyyyyyy, Zone:us-east-1d, Type:gp2, Iops:2400, Is Encrypted:False
New snapshot created: snap-052d1a0f6ea28f78e
++
Waiting for snap-052d1a0f6ea28f78e to become available ...
++
New encrypted snapshot created: snap-02af9c35e86191c0b
++
Waiting for snap-02af9c35e86191c0b to become available ...
++
New encrypted volume created: vol-11111111111111111
++
Waiting for vol-11111111111111111 to become available ...
++
Detaching orignal volume : vol-yyyyyyyy
Waiting for vol-yyyyyyyy to become detached ...
++
Attaching encrypted volume : vol-11111111111111111
++
Waiting for vol-11111111111111111 to become attached ...
++
New encrypted volume attached: vol-11111111111111111
++
Cleaning up snapshot : snap-052d1a0f6ea28f78e
Cleaning up snapshot : snap-02af9c35e86191c0b
Working on Volume:vol-zzzzzzzz, Zone:us-east-1d, Type:gp2, Iops:600, Is Encrypted:False
New snapshot created: snap-01649793841f90ef6
++
Waiting for snap-01649793841f90ef6 to become available ...
++
New encrypted snapshot created: snap-0559c4e39839d9d69
++
Waiting for snap-0559c4e39839d9d69 to become available ...
++
New encrypted volume created: vol-22222222222222222
++
Waiting for vol-22222222222222222 to become available ...
++
Detaching orignal volume : vol-zzzzzzzz
Waiting for vol-zzzzzzzz to become detached ...
++
Attaching encrypted volume : vol-22222222222222222
++
Waiting for vol-22222222222222222 to become attached ...
++
New encrypted volume attached: vol-22222222222222222
++
Cleaning up snapshot : snap-01649793841f90ef6
Cleaning up snapshot : snap-0559c4e39839d9d69
Working on Volume:vol-qqqqqqqq, Zone:us-east-1d, Type:io1, Iops:5000, Is Encrypted:False
New snapshot created: snap-04519e74e1fb7d809
++
Waiting for snap-04519e74e1fb7d809 to become available ...
++
New encrypted snapshot created: snap-03534ca5a21e778ba
++
Waiting for snap-03534ca5a21e778ba to become available ...
++
New encrypted volume created: vol-33333333333333333
++
Waiting for vol-33333333333333333 to become available ...
++
Detaching orignal volume : vol-qqqqqqqq
Waiting for vol-qqqqqqqq to become detached ...
++
Attaching encrypted volume : vol-33333333333333333
++
Waiting for vol-33333333333333333 to become attached ...
++
New encrypted volume attached: vol-33333333333333333
++
Cleaning up snapshot : snap-04519e74e1fb7d809
Cleaning up snapshot : snap-03534ca5a21e778ba
Working on Volume:vol-wwwwwwww, Zone:us-east-1d, Type:io1, Iops:5000, Is Encrypted:False
New snapshot created: snap-0b1f9440fbbacc8df
++
Waiting for snap-0b1f9440fbbacc8df to become available ...
++
New encrypted snapshot created: snap-0afb53828cfbd78ff
++
Waiting for snap-0afb53828cfbd78ff to become available ...
An error occurred (RequestLimitExceeded) when calling the DescribeSnapshots operation (reached max retries: 4): Request limit exceeded.
++
New encrypted volume created: vol-44444444444444444
++
Waiting for vol-44444444444444444 to become available ...
++
Detaching orignal volume : vol-wwwwwwww
Waiting for vol-wwwwwwww to become detached ...
++
Attaching encrypted volume : vol-44444444444444444
++
Waiting for vol-44444444444444444 to become attached ...
++
New encrypted volume attached: vol-44444444444444444
++
Cleaning up snapshot : snap-0b1f9440fbbacc8df
Cleaning up snapshot : snap-0afb53828cfbd78ff
Working on Volume:vol-ffffffff, Zone:us-east-1d, Type:io1, Iops:5000, Is Encrypted:False
New snapshot created: snap-0c2795294db6e45b0
++
Waiting for snap-0c2795294db6e45b0 to become available ...
++
New encrypted snapshot created: snap-00cc20a40532b558b
++
Waiting for snap-00cc20a40532b558b to become available ...
++
New encrypted volume created: vol-55555555555555555
++
Waiting for vol-55555555555555555 to become available ...
++
Detaching orignal volume : vol-ffffffff
Waiting for vol-ffffffff to become detached ...
++
Attaching encrypted volume : vol-55555555555555555
++
Waiting for vol-55555555555555555 to become attached ...
++
New encrypted volume attached: vol-55555555555555555
++
Cleaning up snapshot : snap-0c2795294db6e45b0
Cleaning up snapshot : snap-00cc20a40532b558b
Working on Volume:vol-aaaaaaaa, Zone:us-east-1d, Type:gp2, Iops:4608, Is Encrypted:False
New snapshot created: snap-0f0878b1ce7e2a091
++
Waiting for snap-0f0878b1ce7e2a091 to become available ...
++
New encrypted snapshot created: snap-02550b31663a1c748
++
Waiting for snap-02550b31663a1c748 to become available ...
++
New encrypted volume created: vol-66666666666666666
++
Waiting for vol-66666666666666666 to become available ...
++
Detaching orignal volume : vol-aaaaaaaa
Waiting for vol-aaaaaaaa to become detached ...
++
Attaching encrypted volume : vol-66666666666666666
++
Waiting for vol-66666666666666666 to become attached ...
++
New encrypted volume attached: vol-66666666666666666
++
Cleaning up snapshot : snap-0f0878b1ce7e2a091
Cleaning up snapshot : snap-02550b31663a1c748
Working on Volume:vol-dddddddd, Zone:us-east-1d, Type:gp2, Iops:3072, Is Encrypted:False
New snapshot created: snap-069eaf9b87d696d23
++
Waiting for snap-069eaf9b87d696d23 to become available ...
++
New encrypted snapshot created: snap-09969539b2c36d354
++
Waiting for snap-09969539b2c36d354 to become available ...
++
New encrypted volume created: vol-77777777777777777
++
Waiting for vol-77777777777777777 to become available ...
++
Detaching orignal volume : vol-dddddddd
Waiting for vol-dddddddd to become detached ...
++
Attaching encrypted volume : vol-77777777777777777
++
Waiting for vol-77777777777777777 to become attached ...
++
New encrypted volume attached: vol-77777777777777777
++
Cleaning up snapshot : snap-069eaf9b87d696d23
Cleaning up snapshot : snap-09969539b2c36d354

```
