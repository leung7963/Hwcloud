import requests
from huaweicloudsdkdns.v2 import *
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkcore.http.http_config import HttpConfig
from huaweicloudsdkcore.client import Client

# 设置华为云的AK和SK
ak = 'your-access-key'
sk = 'your-secret-key'
project_id = 'your-project-id'
zone_id = 'your-zone-id'  # DNS Zone ID
domain_name = 'your-domain.com'  # 你要操作的域名

# 创建客户端
credentials = BasicCredentials(ak, sk, project_id)
config = HttpConfig.get_default_config()
client = DnsClient.new_builder() \
    .with_credentials(credentials) \
    .with_http_config(config) \
    .build()

# 删除域名下所有DNS记录
try:
    list_record_sets_request = ListRecordSetsRequest(zone_id=zone_id)
    record_sets = client.list_record_sets(list_record_sets_request).recordsets

    for record_set in record_sets:
        delete_record_set_request = DeleteRecordSetRequest(zone_id=zone_id, recordset_id=record_set.id)
        client.delete_record_set(delete_record_set_request)
    print("已删除所有DNS记录。")
except exceptions.ClientRequestException as e:
    print(f"删除DNS记录时出现错误: {e.status_code} - {e.error_msg}")

# 从URL获取IP地址
try:
    response = requests.get('https://raw.githubusercontent.com/leung7963/iptest/main/proxyip.txt')
    ip_list = response.text.splitlines()
    print("已获取IP地址列表。")
except requests.RequestException as e:
    print(f"获取IP地址时出现错误: {str(e)}")
    ip_list = []

# 创建新的DNS记录
try:
    for ip in ip_list:
        create_record_set_req = CreateRecordSetRequest(
            zone_id=zone_id,
            body=CreateRecordSetReq(
                name=domain_name,
                type='A',
                ttl=300,
                records=[ip]
            )
        )
        client.create_record_set(create_record_set_req)
    print("已创建新的DNS记录。")
except exceptions.ClientRequestException as e:
    print(f"创建DNS记录时出现错误: {e.status_code} - {e.error_msg}")
