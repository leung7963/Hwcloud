import os
import requests
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkcore.http.http_config import HttpConfig
from huaweicloudsdkcore.region.region import Region
from huaweicloudsdkdns.v2 import *
from huaweicloudsdkdns.v2.region.dns_region import DnsRegion
from huaweicloudsdkdns.v2.model.create_record_set_req import CreateRecordSetReq  # 确保导入正确的类

# 设置华为云的AK和SK
ak = os.environ["HUAWEI_ACCESS_KEY"]
sk = os.environ["HUAWEI_SECRET_KEY"]
project_id = 'c339558c4a1f4b9c850e52933ae5012f'
zone_id = 'ff808082915709880191909e06b005cb'  # DNS Zone ID
domain_name = 'proxyip.leung0108.us.kg'  # 你要操作的域名


# 设置区域，例如：华北-北京四（cn-north-4），根据实际情况设置
region = 'ap-southeast-1'

# 创建客户端
credentials = BasicCredentials(ak, sk, project_id)
config = HttpConfig.get_default_config()

client = DnsClient.new_builder() \
    .with_credentials(credentials) \
    .with_region(Region(region, f"https://dns.{region}.myhuaweicloud.com")) \
    .with_http_config(config) \
    .build()

# 删除域名下所有可删除的DNS记录
try:
    list_record_sets_request = ListRecordSetsRequest()
    list_record_sets_request.zone_id = zone_id
    record_sets = client.list_record_sets(list_record_sets_request).recordsets

    for record_set in record_sets:
        if record_set.status != "ACTIVE" or record_set.name == "@." + domain_name or record_set.name == "www." + domain_name:
            # 跳过不可删除的记录集
            print(f"跳过默认记录集: {record_set.name}")
            continue

        delete_record_set_request = DeleteRecordSetRequest(
            zone_id=zone_id, 
            recordset_id=record_set.id
        )
        client.delete_record_set(delete_record_set_request)
        print(f"已删除记录集: {record_set.name}")
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
        create_record_set_request = CreateRecordSetRequest(
            zone_id=zone_id,
            body={
                "name": domain_name,
                "type": "A",
                "ttl": 300,
                "records": [ip]
            }
        )
        response = client.create_record_set(create_record_set_request)
        print(f"已创建新的DNS记录: {ip}")
except exceptions.ClientRequestException as e:
    print(f"创建DNS记录时出现错误: {e.status_code} - {e.error_msg}")