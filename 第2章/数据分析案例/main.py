
from data_define import Record
from file_define import FileReader,CsvReader,JsonReader
from pathlib import Path

from pyecharts.charts import Bar
from pyecharts.options import *
from pyecharts.globals import ThemeType

base_dir = Path(__file__).resolve().parent

csvReader = CsvReader(str(base_dir / "resource" / "order_data.cvs"))
jsonReader = JsonReader(str(base_dir / "resource" / "order_data.json"))

csv_data:list[Record] = csvReader.read_date()
json_data:list[Record] = jsonReader.read_date()
all_data = csv_data + json_data

all_data_dict = {}

for record in all_data:
    if record.data in all_data_dict.keys():
        all_data_dict[record.data] += record.money
    else:
        all_data_dict[record.data] = record.money

# 可视化图表
bar = Bar(init_opts=InitOpts(theme=ThemeType.LIGHT))

bar.add_xaxis(list(all_data_dict.keys()))
bar.add_yaxis("订单金额", list(all_data_dict.values()), label_opts=LabelOpts(is_show=False))
bar.set_global_opts(title_opts=TitleOpts(title="每日销售额"))
bar.render("每日销售额柱状图.html")