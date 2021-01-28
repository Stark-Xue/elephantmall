from fdfs_client.client import Fdfs_client
client = Fdfs_client('elephantmall/utils/fastdfs/client.conf')
ret = client.upload_by_filename('/Users/severen/Downloads/666.jpg')
print(ret)