import requests
import os
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkdns.v2.region.dns_region import DnsRegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkdns.v2 import *

domain = 'leung0108.us.kg'
def get_ip_list(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text.strip().split('\n')

def get_huawei_zone_id(client):
    # 根据实际情况调整查询条件获取域名的 zone_id
    request = ShowRecordSetByZoneRequest()
    response = client.show_record_set_by_zone(request)
    # 假设这里第一个结果的 zone_id 就是要找的，实际情况可能需要更复杂的逻辑
    if response.zones:
        return response.zones[0].id
    else:
        raise Exception("No zones found")
def get_huawei_record_id(client):
    # 根据实际情况调整查询条件获取域名的 zone_id
    request = ListRecordSetsRequest(zone_id=zone_id)
    response = client.list_record_sets(request)
    # 假设这里第一个结果的 zone_id 就是要找的，实际情况可能需要更复杂的逻辑
    if response.recordsets:
        return response.recordsets[0].id
    else:
        raise Exception("No zones found")
        
        
def delete_existing_dns_records(client, zone_id, recordset_id, subdomain, domain):
    request = BatchDeleteRecordSetWithLineRequest()
    listRecordsetIdsbody = ['{recordset_id}']
    request.body = BatchDeleteRecordSetWithLineRequestBody(recordset_ids=listRecordsetIdsbody)
    response = client.batch_delete_record_set_with_line(request)
    print(response)

def update_huawei_dns(ip_list, client, zone_id, recordset_id, subdomain, domain):
    record_name = domain if subdomain == '@' else f'{subdomain}.{domain}'
    for ip in ip_list:
        request = CreateRecordSetRequest(
            zone_id=zone_id,
            body={
                "name": record_name,
                "description": "",
                "type": "A",
                "ttl": 60,
                "records": [ip]
            }
        )
        response = client.create_record_set(request)
        if response.status_code == 200:
            print(f"Add {subdomain}:{ip}")
        else:
            print(f"Failed to add A record for IP {ip} to subdomain {subdomain}: {response.status_code} {response.text}")

if __name__ == "__main__":
    # 华为云认证信息设置
    ak = os.getenv('HUAWEI_ACCESS_KEY')
    sk = os.getenv('HUAWEI_SECRET_KEY')
    credentials = BasicCredentials(ak, sk)
    client = DnsClient.new_builder().with_credentials(credentials).with_region(DnsRegion.value_of("ap-southeast-1")).build()
    
    # 示例 URL 和子域名对应的 IP 列表
    subdomain_ip_mapping = {
        'proxyip': 'https://raw.githubusercontent.com/leung7963/iptest/main/proxyip.txt',
        # 添加更多子域名和对应的 IP 列表 URL
    }
    
    try:
        # 获取华为云域区 ID 和域名
        zone_id = get_huawei_zone_id(client)
        recordset_id = get_huawei_record_id(client)
        
        for subdomain, url in subdomain_ip_mapping.items():
            # 获取 IP 列表
            ip_list = get_ip_list(url)
            # 删除现有的 DNS 记录
            delete_existing_dns_records(client, zone_id, subdomain, domain)
            # 更新华为云 DNS 记录
            update_huawei_dns(ip_list, client, zone_id, subdomain, domain)
            
    except Exception as e:
        print(f"Error: {e}")