#!/usr/bin/env python3

import boto3
import sys
import time
from datetime import datetime
from botocore.exceptions import ClientError


#
# Connect AWS
#
def connect_aws(vvProfile,vvRegion,vvService):
    try:
        boto3.setup_default_session(profile_name=vvProfile,region_name=vvRegion)
        worker = boto3.client(vvService)
        return worker
    except ClientError as e:
        print(e)

#
# Find Volumes
#
def find_volumes(vvWorker,vvInstanceId):
    try:
        volume_list=[]
        response=vvWorker.describe_instances(InstanceIds=[vvInstanceId,],)
        for item in response['Reservations']:
            for subitem in item['Instances']:
                vvRootDevice=subitem['RootDeviceName']
                for lastitem in subitem['BlockDeviceMappings']:
                    for key,value in lastitem.items():
                        vvDeviceName=lastitem['DeviceName']
                        if key == 'Ebs':
                            if not vvDeviceName == vvRootDevice:
                                vvVolumeId=lastitem['Ebs'].get("VolumeId")
                                az_response=vvWorker.describe_volumes(VolumeIds=[vvVolumeId,])
                                vvVolumeZone=az_response['Volumes'][0]['AvailabilityZone']
                                volume_list.append([vvDeviceName,vvVolumeId,vvVolumeZone])
        return volume_list
    except ClientError as e:
        print(e)

#
# Create SnapShot
#
def create_snapshot(vvWorker,vvVolumeId):
    try:
        create_s_response = vvWorker.create_snapshot(VolumeId=vvVolumeId)
        return create_s_response['SnapshotId']
    except ClientError as e:
        print(e)
#
# Copy SnapShot
#
def copy_snapshot(vvWorker,vvSnapshotId,vvKmsKeyId):
    try:
        copy_response = vvWorker.copy_snapshot(Encrypted=True,
                KmsKeyId=vvKmsKeyId,
                SourceRegion='us-east-1',
                SourceSnapshotId=vvSnapshotId,
                DryRun=False)
        return copy_response['SnapshotId']
    except ClientError as e:
        print(e)

#
# SnapShot Status
#
def snapshot_status(vvWorker,vvSnapshotId):
    try:
        status_s_response = vvWorker.describe_snapshots(SnapshotIds=[ vvSnapshotId, ], DryRun=False)
        return status_s_response['Snapshots'][0]['State']
    except ClientError as e:
        print(e)

#
# Create New Volume gp2
#
def create_volume_gp2(vvWorker,vvSnapshotId,vvVolumeZone,vvVolumeType):
    try:
        create_v_response = vvWorker.create_volume(AvailabilityZone=vvVolumeZone,SnapshotId=vvSnapshotId,VolumeType=vvVolumeType)
        return create_v_response['VolumeId']
    except ClientError as e:
        print(e)

#
# Create New Volume Io1
#
def create_volume_io1(vvWorker,vvSnapshotId,vvVolumeZone,vvVolumeType,vvVolumeIops):
    try:
        create_v_response = vvWorker.create_volume(AvailabilityZone=vvVolumeZone,Iops=vvVolumeIops,SnapshotId=vvSnapshotId,VolumeType=vvVolumeType)
        return create_v_response['VolumeId']
    except ClientError as e:
        print(e)

#
# Volume Status
#
def volume_status(vvWorker,vvVolumeId):
    try:
        status_v_response = vvWorker.describe_volumes(VolumeIds=[ vvVolumeId,])
        return status_v_response['Volumes'][0]['State']
    except ClientError as e:
        print(e)

#
# Volume Specs
#
def volume_specs(vvWorker,vvVolumeId):
    try:
        specs_v_response = vvWorker.describe_volumes(VolumeIds=[ vvVolumeId,])
        return [specs_v_response['Volumes'][0]['VolumeType'],specs_v_response['Volumes'][0]['Iops'],specs_v_response['Volumes'][0]['Encrypted']]
    except ClientError as e:
        print(e)

#
# Detach Volume
#
def detach_volume(vvWorker,vvVolumeId):
    try:
        detach_v_response = vvWorker.detach_volume(VolumeId=vvVolumeId)
        return detach_v_response['VolumeId']
    except ClientError as e:
        print(e)

#
# Attach Volume
#
def attach_volume(vvWorker,vvDeviceName,vvInstanceId,vvVolumeId):
    try:
        attach_v_response = vvWorker.attach_volume(Device=vvDeviceName,InstanceId=vvInstanceId,VolumeId=vvVolumeId)
        return attach_v_response['VolumeId']
    except ClientError as e:
        print(e)

def delete_snapshot(vvWorker,vvSnapId):
      try:
          snapshot_delete_response = vvWorker.delete_snapshot(SnapshotId=vvSnapId)
          return snapshot_delete_response
      except ClientError as e:
          print(e)

def find_kms_key(vvWorker):
      try:
          key_response = vvWorker.list_aliases()
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
    print('++')

#
# ~~~~~~~~~~ MAIN STARTS HERE ~~~~~~~~~~~
#
if __name__ == '__main__':
    #
    # Check number of arguments
    #
    check_args()
    #
    # Set vars
    #
    vProfile=sys.argv[1]
    vRegion=sys.argv[2]
    vInstanceId=sys.argv[3]
    vSnapshotStatus=""
    vVolumeStatus=""
    #
    # Connect AWS
    #
    worker_ec2=connect_aws(vProfile,vRegion,'ec2')
    worker_kms=connect_aws(vProfile,vRegion,'kms')
    #
    # Find aws/ebs key of the account
    # Will be used in copy_snapshot
    #
    vEbsKey=find_kms_key(worker_kms)
    print(f'Following aws/ebs encryption key will be used:')
    print(f'{vEbsKey}')
    #
    # If only attached volume is boot/root volume, don't touch it
    #
    vSourceVolumeList=find_volumes(worker_ec2,vInstanceId)
    if not vSourceVolumeList:
        print(f'Instance has only one boot ebs volume ...')
        exit()
    else:
        print(f'Following volumes found:')
        for vol in vSourceVolumeList:
            print(vol)
    # vol[0] --> Device Name
    # vol[1] --> Volume ID
    # vol[2] --> Volume Zone
    for vol in vSourceVolumeList:
        vActiveDeviceName=vol[0]
        vActiveVolume=vol[1]
        vActiveVolumeZone=vol[2]
        #
        # Find if volume is encrypted or Io1 volume
        #
        vActiveVolumeSpecs=volume_specs(worker_ec2,vActiveVolume)
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
            print(f'{vActiveVolume} is already encrypted..')
        else:
            #
            # Create Snapshot
            #
            vSourceSnapshot=create_snapshot(worker_ec2,vActiveVolume)
            print(f'New snapshot created: {vSourceSnapshot}')
            seperator()
            #
            # Wait till snapshot becomes available
            #
            print(f'Waiting for {vSourceSnapshot} to become available ...')
            vSnapshotStatus=""
            while vSnapshotStatus != "completed":
                vSnapshotStatus=snapshot_status(worker_ec2,vSourceSnapshot)
                time.sleep(60)
            seperator()
            #
            # Encrypt Snapshot
            #
            vEncryptedSnapshot=copy_snapshot(worker_ec2,vSourceSnapshot,vEbsKey)
            print(f'New encrypted snapshot created: {vEncryptedSnapshot}')
            seperator()
            #
            # Wait till new snapshot becomes available
            #
            print(f'Waiting for {vEncryptedSnapshot} to become available ...')
            vSnapshotStatus=""
            while vSnapshotStatus != "completed":
                vSnapshotStatus=snapshot_status(worker_ec2,vEncryptedSnapshot)
                time.sleep(60)
            seperator()
            #
            # Create New Volume
            #
            if vActiveVolumeType == 'io1':
                vEncryptedVolume=create_volume_io1(worker_ec2,vEncryptedSnapshot,vActiveVolumeZone,vActiveVolumeType,vActiveVolumeIops)
                print(f'New encrypted volume created: {vEncryptedVolume}')
            elif vActiveVolumeType == 'gp2':
                vEncryptedVolume=create_volume_gp2(worker_ec2,vEncryptedSnapshot,vActiveVolumeZone,vActiveVolumeType)
                print(f'New encrypted volume created: {vEncryptedVolume}')
            else:
                print(f'Sorry I do not know how to work on this volume type yet ..')
                exit()
            seperator()
            #
            # Wait till volume becomes available
            #
            print(f'Waiting for {vEncryptedVolume} to become available ...')
            vVolumeStatus=""
            while vVolumeStatus != "available":
                vVolumeStatus=volume_status(worker_ec2,vEncryptedVolume)
                time.sleep(60)
            seperator()
            #
            # Detach Original Volume
            #
            print(f'Detaching orignal volume : {vActiveVolume}')
            vDetachVolume=detach_volume(worker_ec2,vActiveVolume)
            #
            # Wait till volume becomes available
            #
            print(f'Waiting for {vActiveVolume} to become detached ...')
            vVolumeStatus=""
            while vVolumeStatus != "available":
                vVolumeStatus=volume_status(worker_ec2,vActiveVolume)
                time.sleep(60)
            seperator()
            #
            # Attach Original Volume
            #
            print(f'Attaching encrypted volume : {vEncryptedVolume}')
            seperator()
            vAttachVolume=attach_volume(worker_ec2,vActiveDeviceName,vInstanceId,vEncryptedVolume)
            #
            # Wait till volume becomes attached
            #
            print(f'Waiting for {vEncryptedVolume} to become attached ...')
            seperator()
            vVolumeStatus=""
            while vVolumeStatus != "in-use":
                vVolumeStatus=volume_status(worker_ec2,vEncryptedVolume)
                time.sleep(60)
            print(f'New encrypted volume attached: {vEncryptedVolume}')
            seperator()
            print(f'Cleaning up snapshot : {vSourceSnapshot}')
            vDeleteSnapshot=delete_snapshot(worker_ec2,vSourceSnapshot)
            print(f'Cleaning up snapshot : {vEncryptedSnapshot}')
            vDeleteSnapshot=delete_snapshot(worker_ec2,vEncryptedSnapshot)
