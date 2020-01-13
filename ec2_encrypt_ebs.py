#!/usr/bin/env python3
import boto3
import sys
import time
import os
from botocore.exceptions import ClientError
from multiprocessing import Process
#
# Connect AWS
#
def connect_aws(vProfile,vRegion,vService):
    try:
        boto3.setup_default_session(profile_name=vProfile,region_name=vRegion)
        worker = boto3.client(vService)
        return worker
    except ClientError as e:
        print(e)
#
# Find Volumes
#
def find_volumes(vWorker,vInstanceId):
    try:
        vVolume_list=[]
        response=vWorker.describe_instances(InstanceIds=[vInstanceId,],)
        for item in response['Reservations']:
            for subitem in item['Instances']:
                vRootDevice=subitem['RootDeviceName']
                for lastitem in subitem['BlockDeviceMappings']:
                    for key,value in lastitem.items():
                        vDeviceName=lastitem['DeviceName']
                        if key == 'Ebs':
                            if not vDeviceName == vRootDevice:
                                vVolumeId=lastitem['Ebs'].get("VolumeId")
                                az_response=vWorker.describe_volumes(VolumeIds=[vVolumeId,])
                                vVolumeZone=az_response['Volumes'][0]['AvailabilityZone']
                                vVolume_list.append([vDeviceName,vVolumeId,vVolumeZone])
        return vVolume_list
    except ClientError as e:
        print(e)
#
# Create SnapShot
#
def create_snapshot(vWorker,vVolumeId):
    try:
        create_s_response = vWorker.create_snapshot(VolumeId=vVolumeId)
        return create_s_response['SnapshotId']
    except ClientError as e:
        print(e)
#
# Copy SnapShot
#
def copy_snapshot(vWorker,vSnapshotId,vKmsKeyId):
    try:
        copy_response = vWorker.copy_snapshot(Encrypted=True,KmsKeyId=vKmsKeyId,SourceRegion=gRegion,SourceSnapshotId=vSnapshotId,DryRun=False)
        return copy_response['SnapshotId']
    except ClientError as e:
        print(e)
#
# SnapShot Status
#
def snapshot_status(vWorker,vSnapshotId):
    try:
        status_s_response = vWorker.describe_snapshots(SnapshotIds=[ vSnapshotId, ], DryRun=False)
        return status_s_response['Snapshots'][0]['State']
    except ClientError as e:
        print(e)

#
# Create New Volume gp2
#
def create_volume_gp2(vWorker,vSnapshotId,vVolumeZone,vVolumeType):
    try:
        create_v_response = vWorker.create_volume(AvailabilityZone=vVolumeZone,SnapshotId=vSnapshotId,VolumeType=vVolumeType)
        return create_v_response['VolumeId']
    except ClientError as e:
        print(e)
#
# Create New Volume Io1
#
def create_volume_io1(vWorker,vSnapshotId,vVolumeZone,vVolumeType,vVolumeIops):
    try:
        create_v_response = vWorker.create_volume(AvailabilityZone=vVolumeZone,Iops=vVolumeIops,SnapshotId=vSnapshotId,VolumeType=vVolumeType)
        return create_v_response['VolumeId']
    except ClientError as e:
        print(e)
#
# Volume Status
#
def volume_status(vWorker,vVolumeId):
    try:
        status_v_response = vWorker.describe_volumes(VolumeIds=[ vVolumeId,])
        return status_v_response['Volumes'][0]['State']
    except ClientError as e:
        print(e)
#
# Volume Specs
#
def volume_specs(vWorker, vVolumeId):
    try:
        specs_v_response = vWorker.describe_volumes(VolumeIds=[ vVolumeId,])
        return [specs_v_response['Volumes'][0]['VolumeType'],specs_v_response['Volumes'][0]['Iops'],specs_v_response['Volumes'][0]['Encrypted']]
    except ClientError as e:
        print(e)
#
# Detach Volume
#
def detach_volume(vWorker,vVolumeId):
    try:
        detach_v_response = vWorker.detach_volume(VolumeId=vVolumeId)
        return detach_v_response['VolumeId']
    except ClientError as e:
        print(e)
#
# Attach Volume
#
def attach_volume(vWorker,vDeviceName,vInstanceId,vVolumeId):
    try:
        attach_v_response = vWorker.attach_volume(Device=vDeviceName,InstanceId=vInstanceId,VolumeId=vVolumeId)
        return attach_v_response['VolumeId']
    except ClientError as e:
        print(e)
#
# Delete SnapShot
#
def delete_snapshot(vWorker,vSnapId):
      try:
          snapshot_delete_response = vWorker.delete_snapshot(SnapshotId=vSnapId)
          return snapshot_delete_response
      except ClientError as e:
          print(e)
#
# Find KMS Key
#
def find_kms_key(vWorker):
      try:
          key_response = vWorker.list_aliases()
          #print(key_response)
          for item in key_response['Aliases']:
              if item['AliasName'] == 'alias/aws/ebs':
                  return item['AliasArn']
      except ClientError as e:
          print(e)

def check_args():
    if len(sys.argv) < 4:
        print(f'Usage: {sys.argv[0]} profile-name region-name instance-id')
        exit()

def seperator():
    print(f'++{os.getpid()}++')
#
# Change waiting time here
#
def time2sleep():
    time.sleep(60)
#
# Main Function
#
def encrypt_volume(vWorker, vVol, vProfile, vRegion, vEbsKey, vInstanceId):
    ## This function is to encrypt ebs volumes.
    print(f'Encrypting volume: {vVol}')
    vActiveDeviceName=vVol[0]
    vActiveVolume=vVol[1]
    vActiveVolumeZone=vVol[2]
    #
    # Find if volume is encrypted or Io1 volume
    #
    vActiveVolumeSpecs=volume_specs(vWorker, vActiveVolume)
    vActiveVolumeType=vActiveVolumeSpecs[0]
    vActiveVolumeIops=vActiveVolumeSpecs[1]
    vActiveVolumeEncrypted=vActiveVolumeSpecs[2]
    #
    # ActiveVolumeSpecs is a list with [VolumeType,VolumeIops,Encryption:True|False]
    #
    # Debug Print
    print(f'Working on Volume:{vActiveVolume}, Zone:{vActiveVolumeZone}, Type:{vActiveVolumeType}, Iops:{vActiveVolumeIops}, Is Encrypted:{vActiveVolumeEncrypted}')
    #
    # Check if volume is already encrypted
    #
    if vActiveVolumeEncrypted:
        print(f'{vActiveVolume} is already encrypted...')
    else:
        #
        # Create Snapshot
        #
        seperator()
        vSourceSnapshot=create_snapshot(vWorker,vActiveVolume)
        print(f'New snapshot created: {vSourceSnapshot}')
        #
        # Wait till snapshot becomes available
        #
        seperator()
        print(f'Waiting for {vSourceSnapshot} to become available...')
        vSnapshotStatus=""
        while vSnapshotStatus != "completed":
            vSnapshotStatus=snapshot_status(vWorker,vSourceSnapshot)
            time2sleep()
        #
        # Encrypt Snapshot
        #
        seperator()
        vEncryptedSnapshot=copy_snapshot(vWorker,vSourceSnapshot,vEbsKey)
        print(f'New encrypted snapshot created: {vEncryptedSnapshot}')
        #
        # Wait till new snapshot becomes available
        #
        seperator()
        print(f'Waiting for {vEncryptedSnapshot} to become available ...')
        vSnapshotStatus=""
        while vSnapshotStatus != "completed":
            vSnapshotStatus=snapshot_status(vWorker,vEncryptedSnapshot)
            time2sleep()
        #
        # Create New Volume
        #
        if vActiveVolumeType == 'io1':
            vEncryptedVolume=create_volume_io1(vWorker,vEncryptedSnapshot,vActiveVolumeZone,vActiveVolumeType,vActiveVolumeIops)
            seperator()
            print(f'New encrypted volume created: {vEncryptedVolume}')
        elif vActiveVolumeType == 'gp2':
            vEncryptedVolume=create_volume_gp2(vWorker,vEncryptedSnapshot,vActiveVolumeZone,vActiveVolumeType)
            seperator()
            print(f'New encrypted volume created: {vEncryptedVolume}')
        else:
            print(f'Sorry I do not know how to work on this volume type yet...')
            exit()
        #
        # Wait till volume becomes available
        #
        seperator()
        print(f'Waiting for {vEncryptedVolume} to become available...')
        vVolumeStatus=""
        while vVolumeStatus != "available":
            vVolumeStatus=volume_status(vWorker,vEncryptedVolume)
            time2sleep()
        #
        # Detach Original Volume
        #
        seperator()
        print(f'Detaching orignal volume : {vActiveVolume}')
        vDetachVolume=detach_volume(vWorker,vActiveVolume)
        #
        # Wait till volume becomes available
        #
        seperator()
        print(f'Waiting for {vActiveVolume} to become detached...')
        vVolumeStatus=""
        while vVolumeStatus != "available":
            vVolumeStatus=volume_status(vWorker,vActiveVolume)
            time2sleep()
        #
        # Attach Original Volume
        #
        seperator()
        print(f'Attaching encrypted volume : {vEncryptedVolume}')
        vAttachVolume=attach_volume(vWorker,vActiveDeviceName,vInstanceId,vEncryptedVolume)
        #
        # Wait till volume becomes attached
        #
        seperator()
        print(f'Waiting for {vEncryptedVolume} to become attached...')
        vVolumeStatus=""
        while vVolumeStatus != "in-use":
            vVolumeStatus=volume_status(vWorker,vEncryptedVolume)
            time2sleep()
        seperator()
        print(f'New encrypted volume attached: {vEncryptedVolume}')
        seperator()
        print(f'Cleaning up snapshot : {vSourceSnapshot}')
        vDeleteSnapshot=delete_snapshot(vWorker,vSourceSnapshot)
        print(f'Cleaning up snapshot : {vEncryptedSnapshot}')
        vDeleteSnapshot=delete_snapshot(vWorker,vEncryptedSnapshot)
#
# MAIN STARTS HERE
#
if __name__ == '__main__':
    #
    # Check number of arguments
    #
    check_args()
    #
    # Set vars
    #
    gProfile=sys.argv[1]
    gRegion=sys.argv[2]
    gInstanceId=sys.argv[3]
    #
    # Connect AWS
    #
    worker_ec2=connect_aws(gProfile,gRegion,'ec2')
    worker_kms=connect_aws(gProfile,gRegion,'kms')
    #
    # Find aws/ebs key of the account
    # Will be used in copy_snapshot
    #
    gEbsKey=find_kms_key(worker_kms)
    print(f'Following aws/ebs encryption key will be used:')
    print(f'{gEbsKey}')
    #
    # If only attached volume is boot/root volume, don't touch it
    #
    gSourceVolumeList=find_volumes(worker_ec2,gInstanceId)
    if not gSourceVolumeList:
        seperator()
        print(f'Instance has only boot ebs volume...')
        exit()
    else:
        # print(f'Following volumes found:')
        for vol in gSourceVolumeList:
            # 
            # Start encryption process
            #
            p = Process(target=encrypt_volume, args=(worker_ec2, vol, gProfile, gRegion, gEbsKey, gInstanceId,))
            #
            # Leave some time between AWS API requests 
            #
            time.sleep(5)
            p.start()
            p.join(timeout=0)
            #if p.is_alive():
            #    print (f'Process {os.getpid()} is running!')
