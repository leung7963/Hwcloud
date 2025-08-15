import os
import requests
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkcore.http.http_config import HttpConfig
from huaweicloudsdkcore.region.region import Region
from huaweicloudsdkdns.v2 import *
from huaweicloudsdkdns.v2.region.dns_region import DnsRegion
import time
import random

# Set Huawei Cloud credentials
ak = os.environ["HUAWEI_ACCESS_KEY"]
sk = os.environ["HUAWEI_SECRET_KEY"]
project_id = os.environ["PROJECT_ID"]
zone_id = os.environ["ZONE_ID"]  # DNS Zone ID
domain_name = os.environ["DOMAIN_NAME"]  # Domain name to operate on

# Set the region (e.g., 'ap-southeast-1'), based on your situation
region = 'ap-southeast-1'

# Create client
credentials = BasicCredentials(ak, sk, project_id)
config = HttpConfig.get_default_config()

client = DnsClient.new_builder() \
    .with_credentials(credentials) \
    .with_region(Region(region, f"https://dns.{region}.myhuaweicloud.com")) \
    .with_http_config(config) \
    .build()

# Fetch IP addresses from the URL
try:
    response = requests.get('https://raw.githubusercontent.com/leung7963/CFIPS/main/ip.js')
    response.raise_for_status()
    ip_list = response.text.splitlines()
    print(f"Retrieved {len(ip_list)} IP addresses")
    
    # Randomly select 20 IP addresses
    if len(ip_list) > 20:
        ip_list = random.sample(ip_list, 20)
    print(f"Selected {len(ip_list)} random IP addresses: {ip_list}")
except requests.RequestException as e:
    print(f"Error fetching IP addresses: {str(e)}")
    ip_list = []

# Check if any IP addresses were retrieved
if not ip_list:
    print("No IP addresses found, exiting program.")
else:
    # Delete only 'A' records matching the DOMAIN_NAME
    try:
        list_record_sets_request = ListRecordSetsRequest()
        list_record_sets_request.zone_id = zone_id
        record_sets = client.list_record_sets(list_record_sets_request).recordsets

        for record_set in record_sets:
            # Delete only 'A' type records that match DOMAIN_NAME
            if record_set.type == "A" and record_set.name == domain_name + ".":
                delete_record_set_request = DeleteRecordSetRequest(
                    zone_id=zone_id,
                    recordset_id=record_set.id
                )
                try:
                    client.delete_record_set(delete_record_set_request)
                    print(f"Deleted 'A' record: {record_set.name}")
                except exceptions.ClientRequestException as e:
                    if e.status_code == 404:
                        print(f"Record {record_set.name} not found, skipping.")
                    else:
                        print(f"Error deleting DNS record: {e.status_code} - {e.error_msg}")
                # Delay to avoid concurrency issues
                time.sleep(1)
            else:
                print(f"Skipping record: {record_set.name} (type: {record_set.type})")

    except exceptions.ClientRequestException as e:
        print(f"Error retrieving or deleting DNS records: {e.status_code} - {e.error_msg}")

    # Create new 'A' DNS records
    try:
        for ip in ip_list:
            create_record_set_request = CreateRecordSetWithLineRequest(
                zone_id=zone_id,
                body={
                    "name": domain_name + ".",
                    "type": "A",
                    "ttl": 86400,
                    "records": [ip],
                    "weight": "1"
                }
            )
            try:
                response = client.create_record_set_with_line(create_record_set_request)
                print(f"Created new 'A' record: {ip}")
            except exceptions.ClientRequestException as e:
                print(f"Error creating DNS record: {e.status_code} - {e.error_msg}")
            # Delay to avoid concurrency issues
            time.sleep(1)

    except exceptions.ClientRequestException as e:
        print(f"Error creating DNS records: {e.status_code} - {e.error_msg}")
