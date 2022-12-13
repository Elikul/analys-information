import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# читаем данные из файла
ted_talk_df = pd.read_csv("data.csv")

# проверяем на отсутствие каких-то данных и удаляем такие строки для чистого анализа
print(ted_talk_df.isnull().sum())
ted_talk_df.dropna(inplace=True)

# для удобства дату разделить на две колонки, отдельно месяц и отдельно год
months = []
years = []
for date in list(ted_talk_df["date"]):
    months.append(date.split(" ")[0])
    years.append(date.split(" ")[1])

ted_talk_df['month'] = months
ted_talk_df['year'] = years


# округлять до двух знаков после запятой
def round_float_by_2(item):
    return round(item, 2)


# среднее количество просмотров и лайков в каждом году
views_likes_mean = ted_talk_df.groupby("year").mean()
plt.figure(figsize=(12, 8))
plt.title('Среднее количество просмотров и лайков в каждом году', fontsize=12)
# views_likes_mean.plot.bar(subplots=True, rot=45)
sns.scatterplot(data=views_likes_mean, x="likes", y="views", hue="year")
plt.legend(loc="upper center", mode="expand", ncol=10, framealpha=0.2)
plt.savefig("figures/1_views_likes_mean.png")
plt.show()

# зависимость процента лайков среди просмотров от количества просмотров
ted_talk_df["likes_by_views"] = round_float_by_2((ted_talk_df["likes"] / ted_talk_df["views"]) * 100)
ted_talk_df[::150].plot.bar(x="views", y="likes_by_views", figsize=(14, 9), fontsize=6)
plt.title('Зависимость процента лайков среди просмотров от количества просмотров', fontsize=12)
plt.xlabel("Просмотры")
plt.ylabel("Процент лайк/просмотр")
plt.savefig("figures/2_likes_by_views.png")
plt.show()

# общее количество выступлений
fig_count_ted, ax_count_ted = plt.subplots(figsize=(15, 10), nrows=1, ncols=2)
df_count_month = ted_talk_df.month.value_counts().reset_index()
df_count_month.columns = ["month", "counts"]
ax_count_ted[0].pie(x=df_count_month["counts"], labels=df_count_month["month"], radius=1.2, textprops={"fontsize": 6})
ax_count_ted[0].set_title("Общее количество выступлений в месяц", fontsize=12)

df_count_year = ted_talk_df.year.value_counts().reset_index()
df_count_year.columns = ["year", "counts"]
ax_count_ted[1].pie(x=df_count_year["counts"], labels=df_count_year["year"], radius=1.2, textprops={"fontsize": 6})
ax_count_ted[1].set_title("Общее количество выступлений в год", fontsize=12)

plt.savefig("figures/3_count_ted.png")
plt.show()

fig_mean_max, ax_mean_max = plt.subplots(figsize=(15, 8), nrows=1, ncols=3)
# средний процент лайков среди просмотров
likes_by_views_mean = round_float_by_2(ted_talk_df["likes_by_views"].mean())
# среднее количество лайков
likes_mean = round_float_by_2(ted_talk_df["likes"].mean())
# среднее количество просмотров
views_mean = round_float_by_2(ted_talk_df["views"].mean())
# наибольший процент лайков среди просмотров
likes_by_views_max = round_float_by_2(ted_talk_df["likes_by_views"].max())
# наибольшее количество лайков
likes_max = round_float_by_2(ted_talk_df["likes"].max())
# наибольшее количество просмотров
views_max = round_float_by_2(ted_talk_df["views"].max())
ax_mean_max[0].bar(["mean", "max"], [likes_by_views_mean, likes_by_views_max], color=['orange', 'r'])
ax_mean_max[0].set_title("Процент лайков среди просмотров")

ax_mean_max[1].bar(["mean", "max"], [likes_mean, likes_max], color=['orange', 'r'])
ax_mean_max[1].set_title("Количество лайков")

ax_mean_max[2].bar(["mean", "max"], [views_mean, views_max], color=['orange', 'r'])
ax_mean_max[2].set_title("Количество просмотров")

plt.savefig("figures/4_max_mean.png")
plt.show()

# наибольшее количество лайков среди видео, авторы которых выступали только один раз
author_df = ted_talk_df["author"].value_counts().reset_index()
author_df.columns = ["author", "counts"]
max_likes_by_1author = ted_talk_df.loc[ted_talk_df["author"].isin(author_df[author_df["counts"] == 1]["author"])]
fig_author = px.treemap(max_likes_by_1author.sort_values(by="likes").head(10), path=["author", "likes"], names="author",
                        values="likes")
fig_author.update_layout(title="Наибольшее количество лайков среди видео, авторы которых выступали только один раз",
                         title_x=0.5, width=1200, height=480,
                         font_size=16)
fig_author.write_image("figures/5_max_likes_by_1author.png")
fig_author.show()

# зависимость количества просмотров и лайков от даты
views_likes_by_date = ted_talk_df.groupby("date").sum()[["views", "likes"]]
views_likes_by_date.plot.bar(subplots=True, rot=90, figsize=(12, 8),
                             title="Зависимость количества просмотров и лайков от даты", fontsize=4)
plt.savefig("figures/6_views_likes_by_date.png")
plt.show()

# всего просмотров по авторам за 2015 - 2022г.
top_authors_v_list = ted_talk_df.groupby(["author"]).sum().reset_index().sort_values("views", ascending=False).head(20)[
    "author"].to_list()
top_authors_v_df = ted_talk_df[ted_talk_df["author"].isin(top_authors_v_list)].reset_index(drop=True)

fig_author_views = go.Figure()
for year in range(2015, 2023):
    sample = top_authors_v_df.loc[top_authors_v_df["year"] == str(year)].groupby(["author"])[
        "views"].sum().reset_index()
    fig_author_views.add_trace(go.Bar(x=sample["author"], y=sample["views"], name=year))
fig_author_views.update_layout(title="Всего просмотров по авторам за 2015 - 2022г.",
                               title_x=0.5, width=1200, height=480,
                               barmode='stack', paper_bgcolor="#fcfeff", plot_bgcolor="#F1F1F1",
                               xaxis={"categoryorder": "category ascending"})
fig_author_views.write_image("figures/7_top_authors.png")
fig_author_views.show()

# лучшие выступления TED Talks по просмотрам, лайкам и проценту лайков к просмотрам
colors_list = sns.color_palette("deep", n_colors=30).as_hex()
fig_top_ted = make_subplots(rows=2, cols=2, specs=[[{"rowspan": 2, 'type': 'domain'}, {'type': 'domain'}],
                                                   [None, {'type': 'domain'}]])

g_views = ted_talk_df.sort_values('views', ascending=False).head(5)
fig_top_ted.add_trace(go.Pie(labels=g_views['title'], values=g_views['views'], name="Views"), 1, 1)

g_likes = ted_talk_df.sort_values('likes', ascending=False).head(5)
fig_top_ted.add_trace(go.Pie(labels=g_likes['title'], values=g_likes['likes'], name="Likes", marker_colors=colors_list),
                      1, 2)

g_percent_vl = ted_talk_df.sort_values('views', ascending=False).head(1000).sort_values(['likes_by_views'],
                                                                                        ascending=False).head(5)
fig_top_ted.add_trace(go.Pie(labels=g_percent_vl['title'], values=g_percent_vl['likes_by_views'], name="Views"), 2, 2)

fig_top_ted.update_layout(title='Лучшие выступления TED Talks по просмотрам, лайкам и проценту лайков к просмотрам',
                          title_x=0.5, width=1200, height=480,
                          barmode='stack', paper_bgcolor="#fcfeff", plot_bgcolor='#F1F1F1',
                          xaxis={'categoryorder': 'category ascending'})
fig_top_ted.write_image("figures/8_top_titles.png")
fig_top_ted.show()
