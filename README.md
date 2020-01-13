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

Works with gp2 and io1 EBS volumes.  
Starts multiple threads depending on the number of volumes attached to the EC2 instance and the number of CPUs where script is running.  

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

```

# ec2_encrypt_ebs_key_change.py  
AWS EBS volume encryption KMS key change.
Let's say you have used AWS managed KMS key and you need to move your AMI created from your encrypted EC2 instance in to another AWS account.
Then you need to create a Customer Managed KMS key and you need to re-encrypt your EBS volumes with your new key.
 
This is how it goes.  
  - Get new KMS encryption key as an input. 
  - Find all attached EBS volumes.  
  - Exclude root EBS volume.  
  - Check if EBS volume is already encrypted with the provided KMS encryption key.  
  - Get EBS volume type, zone, IOPs values for future use.
  - Create snapshot from the EBS volume.  
  - Create a new encrypted snapshot from the previous snapshot.  
  - Create a new EBS volume from encrypted snapshot.  
  - Detach original EBS volume.  
  - Attach new encrypted EBS volume.  
  - Remove snapshot and encrypted snapshot created from original EBS volume.  
  - Don't touch original EBS volume.  

Works with gp2 and io1 EBS volumes.  
Starts multiple threads depending on the number of volumes attached to the EC2 instance and the number of CPUs where script is running.  

## Requirements
Be sure that target EC2 instance is in "stopped" state.  
Be sure that you have working backups of your EC2 instance.  
Requires AWS profile/region/instance-id as input.  

## 
## Usage
./ec2_encrypt_ebs_key_change profile-name region-name instance-id arn-for-kms-key
