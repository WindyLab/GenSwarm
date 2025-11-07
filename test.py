# -*- coding: utf-8 -*-
"""
作业内容（仅代码版，含详细中文注释）：
- 数据集：Iris（鸢尾花）
- 模型：SVM（分类）、决策树（分类）、朴素贝叶斯（分类）、线性回归（回归）
- 预处理：必要时进行标准化（例如 SVM）
- 训练/测试划分、性能评估与对比
- 结果可视化（混淆矩阵与柱状图），并将关键指标保存为CSV，便于写报告时引用

注意：
1) 线性回归本质为回归算法，不适合用分类指标（accuracy/recall/F1）评估。
   因此本代码将“线性回归”设为单独的“回归任务”：用其它特征预测 “petal length (cm)（花瓣长度）”。
2) 三个分类模型（SVM、决策树、朴素贝叶斯）统一做同一分类任务：预测“species（类别）”，并用准确率、宏平均精确率/召回率/F1 进行比较。
3) 代码中尽量包含详细中文注释，便于理解与报告撰写（可把注释思想直接放到“方法/实验设计/结果分析”小节中）。
"""

import os
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn import datasets
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LinearRegression


# ===========================
# 0. 全局随机种子，确保可复现
# ===========================
def set_global_seed(seed: int = 42):
    """设置全局随机种子，保证结果可重复。"""
    random.seed(seed)
    np.random.seed(seed)


# ===========================
# 1. 数据加载与准备
# ===========================
def load_iris_as_dataframe():
    """
    以 DataFrame 形式加载鸢尾花数据，同时保留 target 名称（species）。
    返回：
        df: 包含特征与类别名的DataFrame
        feature_names: 特征名列表
        target_name: 目标列名（分类任务为 'species'）
        target_mapping: 类别编码到类别名的映射字典（如 0->setosa, 1->versicolor, 2->virginica）
    """
    iris = datasets.load_iris()
    feature_names = iris.feature_names  # ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']
    X = iris.data
    y = iris.target
    target_names = iris.target_names  # ['setosa' 'versicolor' 'virginica']

    df = pd.DataFrame(X, columns=feature_names)
    df["species"] = pd.Series(y).map({i: name for i, name in enumerate(target_names)})

    return df, feature_names, "species", {i: name for i, name in enumerate(target_names)}


# ===========================
# 2. 分类任务：SVM / 决策树 / 朴素贝叶斯
# ===========================
def classification_experiment(df: pd.DataFrame, feature_names, target_col: str, result_dir: str):
    """
    对分类任务进行训练与评估（SVM/决策树/朴素贝叶斯）。
    - 任务：使用全部4个特征预测 species（多分类）
    - 数据划分：Stratified（分层抽样）确保各类别比例一致
    - 预处理：SVM 使用标准化；决策树、朴素贝叶斯一般不强制要求标准化（GaussianNB可不标化）
    - 评估：Accuracy、宏平均 Precision/Recall/F1，且输出分类报告与混淆矩阵
    - 交叉验证：5折，给出交叉验证准确率均值（作为辅助稳定性指标）
    - 输出：保存每个模型的指标到 CSV，并绘制指标对比柱状图
    """
    os.makedirs(result_dir, exist_ok=True)

    # ------- 2.1 构造特征与标签 -------
    X = df[feature_names].values
    y = df[target_col].map({"setosa": 0, "versicolor": 1, "virginica": 2}).values  # 数字化标签，便于训练

    # ------- 2.2 训练/测试集划分（分层抽样，保持类别比例） -------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    # ------- 2.3 定义三个分类器 -------
    # SVM 一般对特征尺度敏感，使用Pipeline加入标准化
    svm_clf = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("svc", SVC(kernel="rbf", C=1.0, gamma="scale", probability=False)),  # RBF核是常用默认选择
        ]
    )

    dt_clf = DecisionTreeClassifier(
        criterion="gini", max_depth=None, random_state=42
    )  # 决策树对尺度不敏感

    nb_clf = GaussianNB()  # 高斯朴素贝叶斯，默认即可

    classifiers = {
        "SVM_RBF": svm_clf,
        "DecisionTree": dt_clf,
        "GaussianNB": nb_clf,
    }

    # ------- 2.4 评估函数 -------
    def evaluate_classifier(name, model, X_tr, y_tr, X_te, y_te):
        """训练并评估单个分类器，返回指标字典与混淆矩阵。"""
        # 训练
        model.fit(X_tr, y_tr)
        # 预测
        y_pred = model.predict(X_te)
        # 基本指标（采用宏平均，兼顾类别不平衡）
        acc = accuracy_score(y_te, y_pred)
        prec = precision_score(y_te, y_pred, average="macro", zero_division=0)
        rec = recall_score(y_te, y_pred, average="macro", zero_division=0)
        f1 = f1_score(y_te, y_pred, average="macro", zero_division=0)

        # 交叉验证（在训练集上做5折交叉验证，报告平均准确率，体现模型稳定性）
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(model, X_tr, y_tr, cv=skf, scoring="accuracy")
        cv_mean = cv_scores.mean()
        cv_std = cv_scores.std()

        # 分类报告（含每类的精确率/召回率/F1）
        report = classification_report(y_te, y_pred, target_names=["setosa", "versicolor", "virginica"], zero_division=0)

        # 混淆矩阵
        cm = confusion_matrix(y_te, y_pred)

        # 保存混淆矩阵图像
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["setosa", "versicolor", "virginica"])
        fig, ax = plt.subplots(figsize=(4.5, 4))
        disp.plot(ax=ax, cmap="Blues", colorbar=False)
        ax.set_title(f"{name} - Confusion Matrix")
        plt.tight_layout()
        fig_path = os.path.join(result_dir, f"{name}_confusion_matrix.png")
        plt.savefig(fig_path, dpi=160)
        plt.close(fig)

        # 返回汇总结果
        metrics = {
            "model": name,
            "accuracy": acc,
            "precision_macro": prec,
            "recall_macro": rec,
            "f1_macro": f1,
            "cv_accuracy_mean_5fold": cv_mean,
            "cv_accuracy_std_5fold": cv_std,
            "classification_report": report,
            "confusion_matrix": cm,
            "confusion_matrix_fig": fig_path,
        }
        return metrics

    # ------- 2.5 逐个模型评估并收集结果 -------
    cls_results = []
    for name, model in classifiers.items():
        metrics = evaluate_classifier(name, model, X_train, y_train, X_test, y_test)
        cls_results.append(metrics)

    # ------- 2.6 将分类指标保存为 CSV，便于写报告引用 -------
    df_cls_metrics = pd.DataFrame(
        [
            {
                "model": m["model"],
                "accuracy": m["accuracy"],
                "precision_macro": m["precision_macro"],
                "recall_macro": m["recall_macro"],
                "f1_macro": m["f1_macro"],
                "cv_accuracy_mean_5fold": m["cv_accuracy_mean_5fold"],
                "cv_accuracy_std_5fold": m["cv_accuracy_std_5fold"],
            }
            for m in cls_results
        ]
    )
    cls_csv_path = os.path.join(result_dir, "classification_metrics.csv")
    df_cls_metrics.to_csv(cls_csv_path, index=False, encoding="utf-8-sig")

    # ------- 2.7 可视化：分类模型的四项指标对比（accuracy/precision/recall/F1） -------
    # 注意：不要设置特定颜色风格，保持默认即可，方便自动化运行环境
    metric_names = ["accuracy", "precision_macro", "recall_macro", "f1_macro"]
    x = np.arange(len(classifiers))  # x 轴为模型
    width = 0.18

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for i, mname in enumerate(metric_names):
        vals = [metrics[mname] for metrics in cls_results]
        ax.bar(x + (i - 1.5) * width, vals, width, label=mname)

    ax.set_xticks(x)
    ax.set_xticklabels([m["model"] for m in cls_results])
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Score")
    ax.set_title("Classification Metrics Comparison (Iris)")
    ax.legend(loc="lower right", ncol=2)
    plt.tight_layout()
    bar_fig_path = os.path.join(result_dir, "classification_metrics_bar.png")
    plt.savefig(bar_fig_path, dpi=160)
    plt.close(fig)

    # ------- 2.8 将每个模型的分类报告打印到控制台（写报告时可粘贴） -------
    for m in cls_results:
        print("========================================")
        print(f"模型：{m['model']}")
        print(f"Accuracy: {m['accuracy']:.4f}")
        print(f"Precision(macro): {m['precision_macro']:.4f}")
        print(f"Recall(macro): {m['recall_macro']:.4f}")
        print(f"F1(macro): {m['f1_macro']:.4f}")
        print(f"5折交叉验证准确率均值±方差: {m['cv_accuracy_mean_5fold']:.4f} ± {m['cv_accuracy_std_5fold']:.4f}")
        print("\n分类报告：\n", m["classification_report"])
        print("混淆矩阵：\n", m["confusion_matrix"])
        print("混淆矩阵图像已保存至：", m["confusion_matrix_fig"])

    return df_cls_metrics, cls_results


# ===========================
# 3. 回归任务：线性回归（用其它特征预测花瓣长度）
# ===========================
def regression_experiment(df: pd.DataFrame, feature_names, result_dir: str):
    """
    线性回归：选择一个连续目标（这里选 'petal length (cm)'），用其余特征进行预测。
    - 数据划分：KFold 或 train_test_split
    - 评估指标：MAE / RMSE / R^2（常见回归指标）
    - 输出：保存指标到 CSV，绘制“真实 vs 预测”散点图
    """
    os.makedirs(result_dir, exist_ok=True)

    # ------- 3.1 构造回归任务的特征与目标 -------
    target_feature = "petal length (cm)"  # 选择要预测的连续变量
    # 使用除目标外的其余特征作为输入
    X_cols = [c for c in feature_names if c != target_feature]
    X = df[X_cols].values
    y = df[target_feature].values

    # ------- 3.2 划分训练/测试集（随机） -------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42
    )

    # ------- 3.3 建模：线性回归（可选是否标准化，线性回归对尺度不太敏感，这里保持原样） -------
    lr = LinearRegression()

    # ------- 3.4 训练 -------
    lr.fit(X_train, y_train)

    # ------- 3.5 预测与评估 -------
    y_pred = lr.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    r2 = r2_score(y_test, y_pred)

    # ------- 3.6 K折交叉验证（5折）作为稳定性参考（以R^2为评分） -------
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(lr, X, y, cv=kf, scoring="r2")
    cv_mean = cv_scores.mean()
    cv_std = cv_scores.std()

    # ------- 3.7 保存回归指标 -------
    df_reg_metrics = pd.DataFrame(
        [
            {
                "model": "LinearRegression",
                "target": target_feature,
                "features": ", ".join(X_cols),
                "MAE": mae,
                "RMSE": rmse,
                "R2": r2,
                "cv_R2_mean_5fold": cv_mean,
                "cv_R2_std_5fold": cv_std,
            }
        ]
    )
    reg_csv_path = os.path.join(result_dir, "regression_metrics.csv")
    df_reg_metrics.to_csv(reg_csv_path, index=False, encoding="utf-8-sig")

    # ------- 3.8 可视化：真实值 vs 预测值 散点图 -------
    fig, ax = plt.subplots(figsize=(4.5, 4))
    ax.scatter(y_test, y_pred, alpha=0.75)
    ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], linestyle="--")
    ax.set_xlabel("真实花瓣长度 (cm)")
    ax.set_ylabel("预测花瓣长度 (cm)")
    ax.set_title("Linear Regression: True vs Predicted")
    plt.tight_layout()
    scatter_path = os.path.join(result_dir, "linear_regression_true_vs_pred.png")
    plt.savefig(scatter_path, dpi=160)
    plt.close(fig)

    # ------- 3.9 控制台输出，便于报告引用 -------
    print("========================================")
    print("线性回归（回归任务）：预测 petal length (cm)")
    print(f"使用特征：{', '.join(X_cols)}")
    print(f"MAE: {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R2: {r2:.4f}")
    print(f"5折交叉验证 R2 均值±方差: {cv_mean:.4f} ± {cv_std:.4f}")
    print("散点图已保存至：", scatter_path)

    return df_reg_metrics


# ===========================
# 4. 主函数：整合流程
# ===========================
def main():
    # 4.1 设置随机种子
    set_global_seed(42)

    # 4.2 结果输出目录（图像与CSV将保存到此处；报告中可直接引用）
    result_dir = "./results_iris"
    os.makedirs(result_dir, exist_ok=True)

    # 4.3 加载数据
    df, feature_names, target_col, target_mapping = load_iris_as_dataframe()

    # 4.4 基础数据检查（可选：保存原始数据为CSV，便于记录）
    raw_csv_path = os.path.join(result_dir, "iris_raw.csv")
    df.to_csv(raw_csv_path, index=False, encoding="utf-8-sig")
    print("原始数据已保存至：", raw_csv_path)

    # 4.5 分类实验：SVM / 决策树 / 朴素贝叶斯
    df_cls_metrics, cls_results = classification_experiment(
        df=df, feature_names=feature_names, target_col=target_col, result_dir=result_dir
    )

    # 4.6 回归实验：线性回归（预测花瓣长度）
    df_reg_metrics = regression_experiment(
        df=df, feature_names=feature_names, result_dir=result_dir
    )

    # 4.7 汇总说明（控制台打印，报告撰写时可参考）
    print("========================================")
    print("分类指标汇总（保存于 classification_metrics.csv ）：")
    print(df_cls_metrics)
    print("回归指标汇总（保存于 regression_metrics.csv ）：")
    print(df_reg_metrics)

    # 4.8 额外可视化：特征直方图/箱线图等（可选，此处不展开，保持作业核心简洁）
    # 如需：可用 df.hist() 或 seaborn（若允许）进行更丰富可视化。
    # 由于作业中未强制要求，此处不再增加依赖与图像。

    print("全部实验完成。请在 ./results_iris 查看CSV与图像文件，用于报告撰写与提交。")


if __name__ == "__main__":
    main()
