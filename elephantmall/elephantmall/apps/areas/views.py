from django.core.cache import cache
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View


from areas.models import Area
from elephantmall.utils import constants
from elephantmall.utils.response_code import RETCODE


class AreaView(View):
    print("hahatesttestha")
    def get(self, request: HttpRequest):
        # 1.提取 area_id
        area_id = request.GET.get('area_id')
        # 2.判断 area_id 是否存在
        # 2.3组织响应数据
        if not area_id:
            province_list = cache.get("province_list")
            if not province_list:
                # 2.1如果前端没有传入area_id，表示用户需要省份数据，那么查询 parent_id 等于 null 的数据
                try:
                    provinces = Area.objects.filter(parent__isnull=True)
                    print("in here!!!!")
                    province_list = []
                    for province in provinces:
                        province_list.append({'id': province.id, 'name': province.name})
                except Exception:
                    return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '省份数据错误'})
                cache.set("province_list", province_list, constants.AREAS_CACHE_EXPIRES)
            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'province_list': province_list})
        else:
            sub_data = cache.get("sub_" + area_id)
            print(sub_data, type(sub_data))
            if not sub_data['subs']:
                # 2.2如果前端传入了area_id，表示用户需要市或区数据，那么查询 parent_id 等于 area_id 的数据
                try:
                    area = Area.objects.get(id=area_id)
                    subs = area.subs.all()
                    subs_list = []
                    for sub in subs:
                        subs_list.append({'id': sub.id, 'name': sub.name})
                    sub_data = {'id': area.id, 'name': area.name, 'subs': subs_list}
                    print("subs_list: ", subs_list)
                except Exception:
                    return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '市区数据错误'})
                cache.set("sub_" + area_id, sub_data, constants.AREAS_CACHE_EXPIRES)
            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'sub_data': sub_data})

        # 3.返回响应