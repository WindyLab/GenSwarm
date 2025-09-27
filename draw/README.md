# Draw 目录说明

本目录包含了 GenSwarm 项目的数据分析、可视化和实验脚本。

## 目录结构

```
draw/
├── scripts/                    # 脚本文件

│   ├── data_processing/        # 数据处理
│   │   ├── multi_model_success_rate_analyzer.py   # 多模型成功率分析器
│   │   └── prompt_type_success_analyzer.py        # 提示类型成功率分析器
│   ├── visualization/          # 可视化
│   │   ├── multi_model_performance_plotter.py     # 多模型性能图表绘制器
│   │   ├── prompt_type_heatmap_plotter.py         # 提示类型热力图绘制器
│   │   ├── robot_tracking_error_analyzer.py       # 机器人跟踪误差分析器
│   │   └── image_overlay_tool.py                  # 图像叠加工具
│   ├── utilities/              # 工具类
│   │   ├── global_local_skill_analyzer.py         # 全局/局部技能分析器
│   │   ├── experiment_result_filter.py            # 实验结果过滤器
│   │   └── lrf_to_mp4_converter.py               # LRF到MP4转换器

├── results/                    # 统一输出目录
│   ├── charts/                 # 图表输出
│   ├── data/                   # 数据输出
│   ├── analysis/               # 分析结果
│   └── logs/                   # 日志文件
├── charts/                     # 历史图表文件
├── data/                       # 历史数据文件
├── logs/                       # 历史日志文件
└── archive/                    # 归档文件
```

## 脚本功能说明

### ORCA算法分析 (orca_analysis/)

- **orca_vs_official_benchmark.py**: 对比自实现的ORCA算法与官方RVO2库的性能基准测试
- **orca_vr_orca_algorithms.py**: ORCA和VR-ORCA算法的核心实现，包含约束构造和速度求解

### 数据处理 (data_processing/)

- **multi_model_success_rate_analyzer.py**: 分析多个AI模型（GPT-4o、O1-mini、Claude、DeepSeek等）的实验成功率
- **prompt_type_success_analyzer.py**: 分析不同提示类型对模型性能的影响
- **experiment_data_processor.py**: 处理实验数据，提取各种方法的成功率并进行基线对比分析

### 可视化 (visualization/)

- **multi_model_performance_plotter.py**: 生成多模型性能对比图表（Figure 1-3）
- **prompt_type_heatmap_plotter.py**: 生成提示类型影响的热力图
- **robot_tracking_error_analyzer.py**: 分析机器人跟踪误差并生成可视化图表
- **image_overlay_tool.py**: 图像叠加处理工具
- **multi_method_performance_visualizer.py**: 多方法性能对比可视化，生成带渐变效果的性能对比图表

### 工具类 (utilities/)

- **global_local_skill_analyzer.py**: 分析全局技能vs局部技能的分布情况
- **experiment_result_filter.py**: 根据条件过滤实验结果目录
- **lrf_to_mp4_converter.py**: 将LRF格式文件转换为MP4格式



## 使用说明

1. **数据处理**: 运行 `data_processing/` 目录下的脚本来处理实验数据
2. **可视化**: 运行 `visualization/` 目录下的脚本来生成图表
3. **输出**: 所有脚本的输出都会保存到 `results/` 目录下的相应子目录中

## 注意事项

- 运行脚本前请确保相关依赖已安装
- 部分脚本需要修改输入数据路径以匹配实际环境
- 所有输出文件都会自动创建必要的目录结构