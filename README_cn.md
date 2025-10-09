- [English Version](https://github.com/wuyao1997/break_axes/blob/main/README.md)

# break_axes：Matplotlib 坐标轴断裂与自定义缩放工具

一个基于 Python 的 Matplotlib 扩展模块，用于实现**坐标轴断裂**（视觉间隙）
与**多区间自定义缩放**功能，适用于展示数值跨度大或存在无关中间区间的数据。


## 模块概述
Matplotlib 原生不支持坐标轴断裂（视觉间隙）和灵活的多区间缩放。
本模块通过一系列易用函数填补了这一空白，主要能力包括：
- 在坐标轴边缘绘制断裂标记以标识数据间隙
- 裁剪坐标轴脊线、线条和绘图元素，隐藏不需要的区间
- 支持多数据区间的线性/对数自定义缩放

## 安装
1.  **从 PyPI 安装**
    ```bash
    pip install break_axes
    ```

2. **本地构建二进制分发包（wheel）**  
   需先安装 `build` 工具：`pip install build`，再执行：
   ```bash
   python -m build
   ```
   会在 `dist/` 目录下生成 `.whl` 格式的二进制包（安装更快）。

3. **本地安装包（开发模式）**  
   用于开发时实时调试，修改代码无需重新安装：
   ```bash
   pip install -e .
   ```


## 核心功能

通常来说，用户只需要使用 `scale_axes` 和 `broken_and_clip_axes` 这两个函数即可。
单如果需要更灵活的设置断裂效果，可能需要阅读源码（不到900行，其中约一半为 docstring）。

| 函数名 | 功能描述 |
| ----- | ---------------------------------- |
| `create_scale` | 用于生成缩放坐标轴的ScaleBase对象                              |
| `scale_axis`   | create_scale的包装函数，用于直接应用缩放                       |
| **`scale_axes`**   | 用于批量应用坐标轴缩放，支持x轴和y轴同时缩放                     |
| `offset_data_point` | 获取指定断裂点对应的断裂标识符顶点坐标                     |
| `xy2points`     | 将输入的x，y点坐标组合为数据点坐标                             |
| `add_broken_line` | 在指定位置添加断裂标记                                      |
| `add_broken_line_in_axis` | 在坐标轴上添加断裂标识                              |
| `get_axis_clip_path` | 获取指定轴的裁剪路径，用于对轴脊进行裁剪                  |
| `get_axes_clip_path` | 获取坐标轴的裁剪路径，用于对坐标轴内artists进行裁剪        |
| `clip_axes`          | 对轴脊和artists进行裁剪                                 |
| **`broken_and_clip_axes`** | `add_broken_line_in_axis` 和 `clip_axes` 的包装     | 


## 依赖环境
- Python 3.8 及以上版本
- Matplotlib 3.5.0 及以上版本  
  安装命令：`pip install matplotlib`


## 快速开始
### 1. 导入模块

```python
import matplotlib.pyplot as plt

from break_axes import __version__, scale_axes, broken_and_clip_axes

plt.rcParams['figure.figsize'] = (3,3)
plt.rcParams['figure.dpi'] = 200
plt.rcParams['axes.linewidth'] = 1.5

print(f"break_axes version: {__version__}")
```

### 2. 多处断裂坐标轴

![multi_break.png](https://raw.githubusercontent.com/wuyao1997/break_axes/main/image/multi_break.png)

```python
fig, ax = plt.subplots(figsize=(4.5,3))
ax.set(xlim=(-32,32), ylim=(0,180), xlabel="x (unit)", ylabel="y (unit)")
ax.set_facecolor("#DDFFAA")
ax.grid(ls=':', lw=0.5, color='dimgray')

# scale x-axis and y-axis to reduce the blank space
scale_axes(ax,
           x_interval=[(-28, -2, 0.01), (2, 28, 0.01)],
           y_interval=[(40,100, 0.1), (100, 180, 0.6)], 
           mode="linear")


_ = ax.set_xticks([-31,-30,-29,-1,0,1,29,30,31])
_ = ax.set_yticks([0,20, 40, 100, 120, 140,160])

rects = ax.bar([-31,-30,-29,-1,0,1,31,30,29], [20,40,22,132,155,108,5,27,17] )
ax.bar_label(rects)

# Text and Annotation wont be clipped
ax.annotate("This is a very long long string.", xy=(-30, 80), xytext=(-30, 168), 
    arrowprops=dict(
        arrowstyle='-|>',
        connectionstyle="arc3,rad=0.1", 
        color='k', 
        shrinkA=5, shrinkB=5
    )
)

# Add broken line in x-axis and y-axis, clip spines and artists in axes
broken_and_clip_axes(ax, x=[-15,15], y=[70], axes_clip=True, which='lower',
                     gap=5, dx=3, dy=3)

# plt.savefig("break_axes_bar.png", transparent=False)
```

### 3. 对数坐标轴

![logscale_break.png](https://raw.githubusercontent.com/wuyao1997/break_axes/main/image/logscale_break.png)

```python
import numpy as np

x = np.logspace(0, 4, 100)

fig, ax = plt.subplots(figsize=(4,3))
ax.set(xlim=(1,10000), ylim=(1,10000), facecolor="#DDFFAA")  
ax.plot(x, x)
ax.set_xticks([1, 10, 100, 500, 5000, 10000],
              [1, 10, 100, 500, 5000, r'$10^4$'])
ax.set_yticks([1, 10, 100, 500, 5000, 10000],
              [1, 10, 100, 500, 5000, r'$10^4$'])

ax.annotate("This is a very long long string.", 
    xy=(5, 10), xytext=(10, 5000), 
    arrowprops=dict(
        arrowstyle='-|>',
        connectionstyle="arc3,rad=0.1", 
        color='k', 
        shrinkA=5, shrinkB=5
    )
)

ax.grid(ls=':')
ax.set_xlabel("X Label")
ax.set_ylabel("Y Label")
ax.set_title("Broken Axis Example - Log Mode")

scale_axes(ax, 
    x_interval=[(600, 4000, 0.1)], 
    y_interval=[(600, 4000, 0.1)],
    mode='log')
broken_and_clip_axes(ax, x=[1500], y=[1500], 
    axes_clip=True, which='lower', gap=5, dx=3, dy=3)

plt.show()
```

### 4. 设置折叠线属性

![schematic_diagram.png](https://raw.githubusercontent.com/wuyao1997/break_axes/main/image/schematic_diagram.png)

![broken_lines_property.png](https://raw.githubusercontent.com/wuyao1997/break_axes/main/image/broken_lines_property.png)

```python
import numpy as np

x = np.logspace(0, 4, 100)

fig, ax = plt.subplots(figsize=(4,3))
ax.set(xlim=(1,10000), ylim=(1,10000), facecolor="#DDFFAA")  
ax.plot(x, x)
ax.set_xticks([1, 10, 100, 500, 5000, 10000],
              [1, 10, 100, 500, 5000, r'$10^4$'])
ax.set_yticks([1, 10, 100, 500, 5000, 10000],
              [1, 10, 100, 500, 5000, r'$10^4$'])

ax.annotate("This is a very long long string.", 
    xy=(5, 10), xytext=(10, 5000), 
    arrowprops=dict(
        arrowstyle='-|>',
        connectionstyle="arc3,rad=0.1", 
        color='k', 
        shrinkA=5, shrinkB=5
    )
)

ax.grid(ls=':')
ax.set_xlabel("X Label")
ax.set_ylabel("Y Label")
ax.set_title("Set Broken Lines Propertye", pad=10)

scale_axes(ax, 
    x_interval=[(600, 4000, 0.1)], 
    y_interval=[(600, 4000, 0.1)],
    mode='log')
broken_lines = broken_and_clip_axes(ax, x=[1500], y=[1500], 
    axes_clip=True, which='both', gap=6, dx=4, dy=4)

bottom_left, bottom_right = broken_lines["bottom"][0]
bottom_left.set(color='r', linewidth=1)
bottom_right.set(color='g', linewidth=1)

left_bottom, left_top = broken_lines["left"][0]
left_bottom.set(color='r', linewidth=2.5)
left_top.set(color='g', linewidth=2.5)

plt.show()
```

## 注意事项
1. **先固定坐标轴范围**：调用断裂/裁剪函数前，必须通过 `ax.set_xlim()` 或 `ax.set_ylim()` 
    固定坐标轴范围——这是确保断裂位置计算准确的关键。
2. **区间规则**：使用 `scale_axes` 时，区间必须**无重叠且按顺序排列**
    （例如 `[(0,2,2), (5,10,1)]` 有效，`[(5,10,1), (0,2,2)]` 无效）。
4. **裁剪排除项**：文本元素（如标签、刻度值）和坐标轴背景（`ax.patch`）不会被裁剪，
    以避免影响可读性。用户也可以使用 `get_axes_clip_path` 自行获取坐标轴裁剪路径，
    参照`clip_axes`函数手动添加需要被裁剪的artists元素。


## 版本与作者
- 版本：0.2.0
- 作者：Wu Yao <wuyao1997@qq.com>