#!/usr/bin/env python3

from subprocess import check_output, STDOUT, run, PIPE
import json

FILTERS = {
    #'description' : 'Created by CreateImage*',
    "owner-id": "insert-owner-id"
}

def main():
    cmd = 'aws ec2 describe-snapshots --profile Stage-EC2Read --filter Name=description,Values="Created by CreateImage*" Name=owner-id,Values=insert-owner-id
    --query "Snapshots[*].{ID:SnapshotId,Vol:VolumeId}"'
    output = check_output(cmd, shell=True, encoding='utf-8')
    loaded_json = json.loads(output)
    
    rm_snapshots = []
    
    for entry in loaded_json:
        snapshot_id = entry.get("ID")
        volume_id = entry.get("Vol")
        
        cmd2 = 'aws ec2 describe-volumes --profile Stage-EC2Read --volume-ids ' + volume_id
        print("Finding orphaned snapshots")
        
        try:
            output = check_output(cmd2, stderr=STDOUT, shell=True, encoding='utf-8')
        except Exception as e:
            if "InvalidVolume.NotFound" in e.output:
                print("Snapshot {} is to be deleted".format(entry['ID']))
                rm_snapshots.append(entry['ID']) 

    if len(rm_snapshots) == 0:
            print("No orphaned snapshots found!")
            return

    print("Exporting orphaned snapshots list to orphanedsnaps.txt...")
    orphsnaps = open('orphanedsnaps.txt', 'w')
    for s_id in rm_snapshots:
        orphsnaps.write(s_id)
        orphsnaps.write("\n")
    orphsnaps.close()
    print("List complete.")
            
if __name__ == "__main__":
    main()
