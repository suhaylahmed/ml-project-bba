"""Export clear, reproducible figures for the dashboard and presentation."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import PrecisionRecallDisplay, RocCurveDisplay

TEAL, ORANGE, INK = "#12616C", "#B64D1B", "#172D35"


def save_figures(folder: Path, y, scores, test: dict, thresholds, importance, comparison):
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.labelcolor": INK, "text.color": INK,
        "figure.facecolor": "white", "savefig.facecolor": "white",
    })
    folder.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 4.6), layout="constrained")
    matrix = np.array([[test["tn"], test["fp"]], [test["fn"], test["tp"]]])
    ax.imshow(matrix, cmap="Blues", vmin=0)
    labels = [["True negative", "False positive"], ["False negative", "True positive"]]
    for row in range(2):
        for col in range(2):
            ax.text(col, row, f"{matrix[row, col]}\n{labels[row][col]}", ha="center", va="center",
                    color="white" if matrix[row, col] > matrix.max() * 0.55 else INK, fontsize=12)
    ax.set(xticks=[0, 1], yticks=[0, 1], xticklabels=["Standard (0)", "Escalate (1)"],
           yticklabels=["Standard (0)", "Escalate (1)"], xlabel="Predicted label", ylabel="Actual proxy label",
           title=f"Frozen test set | threshold {test['threshold']:.2f}")
    fig.savefig(folder / "confusion_matrix.png", dpi=170); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), layout="constrained")
    RocCurveDisplay.from_predictions(y, scores, ax=axes[0], curve_kwargs={"color": TEAL}, name="Selected model")
    axes[0].plot([0, 1], [0, 1], "--", color="#73818A", label="Chance")
    axes[0].set_title("Test ROC curve")
    PrecisionRecallDisplay.from_predictions(y, scores, ax=axes[1], color=TEAL, name="Selected model")
    axes[1].axhline(np.mean(y), ls="--", color=ORANGE, label=f"Positive share {np.mean(y):.2f}")
    axes[1].legend(loc="lower left"); axes[1].set_title("Test precision-recall curve")
    fig.savefig(folder / "roc_precision_recall.png", dpi=170); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4), layout="constrained")
    for key, color in [("recall", TEAL), ("precision", ORANGE), ("f2", "#596579")]:
        ax.plot(thresholds.threshold, thresholds[key], label=key.capitalize(), color=color)
    ax.axvline(test["threshold"], color=INK, ls="--", label="Chosen on validation")
    ax.set(xlabel="Decision threshold", ylabel="Score", ylim=(0, 1.03), title="Validation tradeoffs | test labels not used")
    ax.legend(loc="lower left", ncol=2)
    fig.savefig(folder / "threshold_tradeoff.png", dpi=170); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4), layout="constrained")
    ranked = importance.sort_values("importance_mean")
    ax.barh(ranked.feature.str.replace("_", " "), ranked.importance_mean,
            xerr=ranked.importance_std, color=TEAL, capsize=3)
    ax.axvline(0, color=INK, lw=0.8)
    ax.set(xlabel="Drop in validation average precision when shuffled",
           title="Permutation importance | associations, not causes")
    fig.savefig(folder / "feature_importance.png", dpi=170); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4), layout="constrained")
    ranked = comparison.sort_values("cv_ap_mean")
    ax.barh(ranked.model, ranked.cv_ap_mean, xerr=ranked.cv_ap_std, color=TEAL, capsize=3)
    ax.set(xlim=(0, 1), xlabel="Five-fold training CV average precision (mean +/- SD)",
           title="Model selection | validation and test held aside")
    fig.savefig(folder / "model_comparison.png", dpi=170); plt.close(fig)
