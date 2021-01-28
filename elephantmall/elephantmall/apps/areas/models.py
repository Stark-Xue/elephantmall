from django.db import models

# Create your models here.


class Area(models.Model):
    """
    省市区
    Area实例对象.area_set.all() 查询该区域的所有子级行政列表
    设置了related_name后，就把area_set变成了subs了，Area实例对象.subs.all()
    A 1—— B 多
    A.B_set.all()
    """
    name = models.CharField(max_length=20, verbose_name="区域名称")
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True,
                               verbose_name="父级行政区域")

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '省市区'

    def __str__(self):
        return self.name