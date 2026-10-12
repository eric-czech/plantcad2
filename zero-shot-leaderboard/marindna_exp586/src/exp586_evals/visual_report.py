"""Create the publication figures used in the exp586 PR results report."""

import argparse
import dataclasses
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np
from matplotlib import pyplot as plt

COLORS = {
    "dense": "#64748B",
    "published": "#94A3B8",
    "poe": "#6D5BD0",
}


@dataclasses.dataclass(frozen=True)
class Model:
    key: str
    label: str
    directory: Path
    color: str
    views: frozenset[str]
    result: dict
    method: dict | None


def load_catalog(path: Path) -> list[Model]:
    payload = load(path)
    if payload.get("schema") != 1 or not payload.get("models"):
        raise ValueError("The model catalog must use schema 1 and contain models")
    models = []
    for item in payload["models"]:
        directory = (path.parent / item["result"]).resolve()
        method_path = (
            (path.parent / item["method"]).resolve() if item.get("method") else None
        )
        views = frozenset(item["views"])
        if not (directory / "result.json").is_file():
            raise ValueError(f"Missing result for {item['key']}: {directory}")
        if "methods" in views and (method_path is None or not method_path.is_file()):
            raise ValueError(f"Missing method report for {item['key']}")
        models.append(
            Model(
                key=item["key"],
                label=item["label"],
                directory=directory,
                color=item["color"],
                views=views,
                result=load(directory / "result.json"),
                method=load(method_path) if method_path is not None else None,
            )
        )
    if len({model.key for model in models}) != len(models):
        raise ValueError("Model catalog keys must be unique")
    if len({model.label for model in models}) != len(models):
        raise ValueError("Model catalog labels must be unique")
    return models


def selected(models: list[Model], view: str) -> list[Model]:
    values = [model for model in models if view in model.views]
    if not values:
        raise ValueError(f"Model catalog selects no models for {view}")
    return values
CATEGORIES = (
    "Conservation",
    "Masked motif",
    "Core/non-core",
    "Structural variant",
    "Composite",
)
PUBLISHED = {
    "PlantCAD2-Small": ("PlantCAD2-S", "PlantCAD2-Small"),
    "PlantCAD2-Large": ("PlantCAD2-L", "PlantCAD2-Large"),
    "PlantCAD2.5-Large": ("PlantCAD2.5-L", "PlantCAD2.5-Large"),
    "Evo 2 20B": ("evo2_20b", "evo2_20b"),
}
DENSE_LABELS = {
    "022t": "Dense 0.22T",
    "039t": "Dense 0.39T",
    "056t": "Dense 0.56T",
}
PUBLISHED_TASK_IDS = {
    "conservation_andropogoneae": "cons_andropogoneae",
    "conservation_poaceae_non_tis": "cons_poaceae_nontis",
    "conservation_poaceae_tis": "cons_poaceae_tis",
    "motif_maize_tis": "motif_maize_start_sites",
    "motif_maize_tts": "motif_maize_stop_sites",
    "motif_maize_donor": "motif_maize_donor",
    "motif_maize_acceptor": "motif_maize_acceptor",
    "motif_tomato_tis": "motif_tomato_start_sites",
    "motif_tomato_tts": "motif_tomato_stop_sites",
    "motif_tomato_donor": "motif_tomato_donor",
    "motif_tomato_acceptor": "motif_tomato_acceptor",
    "core_maize_tis": "coreclass_maize_tis",
    "core_maize_tts": "coreclass_maize_tts",
    "core_maize_donor": "coreclass_maize_donor",
    "core_maize_acceptor": "coreclass_maize_acceptor",
    "core_tomato_tis": "coreclass_tomato_tis",
    "core_tomato_tts": "coreclass_tomato_tts",
    "core_tomato_donor": "coreclass_tomato_donor",
    "core_tomato_acceptor": "coreclass_tomato_acceptor",
    "sv_impact": "sv_impact_auprc",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def save(figure: plt.Figure, output: Path, name: str) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for extension in ("png", "svg"):
        target = output / f"{name}.{extension}"
        figure.savefig(
            target,
            dpi=220 if extension == "png" else None,
            bbox_inches="tight",
            facecolor="white",
        )
        if extension == "svg":
            target.write_text(
                "\n".join(line.rstrip() for line in target.read_text().splitlines())
                + "\n"
            )
    plt.close(figure)


def new_profile(result: dict, profile: str = "context-8192") -> dict:
    return result["profiles"][profile]


def overview_series(
    models: list[Model],
    historical: dict,
) -> dict[str, list[float]]:
    series = {
        historical["labels"][rung]: historical["groups"][rung]
        for rung in ("022t", "039t", "056t")
    }
    for label, (_, group_key) in PUBLISHED.items():
        series[label] = historical["published_groups"][group_key]
    for model in selected(models, "overview"):
        groups = new_profile(model.result)["tasks"]["groups"]["natural"]
        series[model.label] = [groups[name] for name in CATEGORIES]
    return series


def model_overview(
    models: list[Model],
    historical: dict,
    output: Path,
) -> None:
    series = overview_series(models, historical)
    labels = list(series)
    values = np.asarray([series[label] for label in labels])
    figure, axes = plt.subplots(
        1,
        2,
        figsize=(13.5, 6.4),
        gridspec_kw={"width_ratios": (1.05, 1.7)},
    )
    composite = values[:, -1]
    order = np.argsort(composite)
    new_colors = {model.label: model.color for model in models}
    colors = [
        new_colors.get(
            label,
            COLORS["dense"] if label.startswith("MarinDNA") else COLORS["published"],
        )
        for label in labels
    ]
    axes[0].barh(
        np.arange(len(labels)),
        composite[order],
        color=np.asarray(colors)[order],
        edgecolor="white",
    )
    axes[0].set_yticks(np.arange(len(labels)), np.asarray(labels)[order])
    axes[0].set_xlabel("20-task composite")
    axes[0].set_xlim(max(0, composite.min() - 0.04), min(1, composite.max() + 0.03))
    axes[0].grid(axis="x", alpha=0.2)
    axes[0].set_axisbelow(True)
    for y, value in enumerate(composite[order]):
        axes[0].text(value + 0.002, y, f"{value:.3f}", va="center", fontsize=8)

    selected = [
        "MarinDNA 1B 0.22T",
        "PlantCAD2-Small",
        "PlantCAD2-Large",
        "PlantCAD2.5-Large",
        "Evo 2 20B",
    ] + [model.label for model in models if "overview_detail" in model.views]
    x = np.arange(4)
    selected_values = []
    for label in selected:
        row = series[label][:-1]
        selected_values.extend(row)
        emphasized = label in new_colors
        axes[1].plot(
            x,
            row,
            marker="o",
            linewidth=2.6 if emphasized else 1.15,
            alpha=1 if emphasized else 0.58,
            label=label,
            color=new_colors.get(label),
        )
    axes[1].set_xticks(x, CATEGORIES[:-1], rotation=18, ha="right")
    axes[1].set_ylabel("Mean task score")
    axes[1].set_ylim(max(0, min(selected_values) - 0.04), 0.9)
    axes[1].grid(axis="y", alpha=0.2)
    axes[1].legend(frameon=False, fontsize=8, ncol=2, loc="lower right")
    figure.suptitle("Exp586 model-family comparison", fontsize=15, weight="bold")
    figure.text(
        0.5,
        0.01,
        "All points use the original full-split PlantCAD2 scoring definition at 8,192 tokens.",
        ha="center",
        color="#475569",
        fontsize=9,
    )
    save(figure, output, "exp586-model-family-overview")


def historical_task_columns(
    historical: dict,
) -> tuple[list[str], dict[str, list[float]]]:
    dense_rows = historical["results"]["022t"]["rows"]
    task_labels = [f"{row['category']} · {row['task']}" for row in dense_rows]
    columns = {
        historical["labels"][rung]: [
            row["selected_value"] for row in historical["results"][rung]["rows"]
        ]
        for rung in ("022t", "039t", "056t")
    }
    for label, (row_key, _) in PUBLISHED.items():
        rows = [row for row in historical["published_rows"] if row["model"] == row_key]
        by_task = {row["task_id"]: float(row["value"]) for row in rows}
        expected = set(PUBLISHED_TASK_IDS.values())
        if len(rows) != len(task_labels) or set(by_task) != expected:
            raise ValueError(f"Published task inventory differs for {label}")
        columns[label] = [by_task[PUBLISHED_TASK_IDS[row["key"]]] for row in dense_rows]
    return task_labels, columns


def task_heatmap(
    models: list[Model],
    historical: dict,
    output: Path,
) -> None:
    labels, historical_columns = historical_task_columns(historical)
    columns = {
        "Dense 0.22T": historical_columns[historical["labels"]["022t"]],
        "PC2 Small": historical_columns["PlantCAD2-Small"],
        "PC2 Large": historical_columns["PlantCAD2-Large"],
        "PC2.5 Large": historical_columns["PlantCAD2.5-Large"],
        "Evo 2 20B": historical_columns["Evo 2 20B"],
    }
    for model in models:
        methods = []
        if "task_natural" in model.views:
            methods.append(("natural", "natural"))
        if "task_two_sided" in model.views:
            methods.append(("two-sided", "bidirectional_poe"))
        if not methods:
            continue
        rows = new_profile(model.result)["tasks"]["rows"]
        if [row["key"] for row in rows] != [
            row["key"] for row in historical["results"]["022t"]["rows"]
        ]:
            raise ValueError(f"New task inventory differs for {model.label}")
        for label, field in methods:
            columns[f"{model.label}\n{label}"] = [row[field] for row in rows]
    names = list(columns)
    values = np.asarray(
        [
            [np.nan if value is None else value for value in columns[name]]
            for name in names
        ]
    ).T
    figure, axis = plt.subplots(figsize=(max(12.6, 1.05 * len(names)), 10.8))
    image = axis.imshow(
        values,
        aspect="auto",
        cmap="viridis",
        vmin=min(0.45, float(np.nanmin(values))),
        vmax=0.9,
    )
    axis.set_xticks(np.arange(len(names)), names, rotation=30, ha="right")
    axis.set_yticks(np.arange(len(labels)), labels, fontsize=8)
    for row in range(values.shape[0]):
        for column in range(values.shape[1]):
            value = values[row, column]
            if np.isfinite(value):
                axis.text(
                    column,
                    row,
                    f"{value:.2f}",
                    ha="center",
                    va="center",
                    fontsize=6.5,
                    color="white" if value < 0.68 else "#111827",
                )
    for boundary in (2.5, 10.5, 18.5):
        axis.axhline(boundary, color="white", linewidth=1.8)
    axis.set_title("Full-split score by task and inference method", weight="bold")
    figure.colorbar(image, ax=axis, fraction=0.025, pad=0.02, label="Task score")
    figure.text(
        0.5,
        0.01,
        "Two-sided = equal-weight product of forward and aligned reverse-complement A/C/G/T probabilities; SV has no centered two-sided definition.",
        ha="center",
        fontsize=8.5,
        color="#475569",
    )
    save(figure, output, "exp586-task-heatmap")


def task_context_deltas(
    models: list[Model],
    output: Path,
) -> None:
    columns = {}
    labels = None
    for model in selected(models, "context"):
        result = model.result
        long_rows = {
            row["key"]: row
            for row in result["profiles"]["context-8192"]["tasks"]["rows"]
        }
        short_rows = result["profiles"]["context-2048"]["tasks"]["rows"]
        current_labels = [f"{row['category']} · {row['task']}" for row in short_rows]
        if labels is None:
            labels = current_labels
        elif labels != current_labels:
            raise ValueError("2,048-token task inventories differ between conditions")
        for label, field in (
            ("natural", "natural"),
            ("two-sided", "bidirectional_poe"),
        ):
            values = []
            for row in short_rows:
                baseline = long_rows[row["key"]]
                if row[field] is None or baseline[field] is None:
                    raise ValueError("Context delta requires paired task values")
                values.append(row[field] - baseline[field])
            columns[f"{model.label}\n{label}"] = values
    values = np.asarray(list(columns.values())).T
    limit = max(0.03, float(np.quantile(np.abs(values), 0.98)))
    figure, axis = plt.subplots(figsize=(4.0 + 1.35 * len(columns), 10.3))
    image = axis.imshow(
        values,
        aspect="auto",
        cmap="RdBu_r",
        vmin=-limit,
        vmax=limit,
    )
    axis.set_xticks(np.arange(len(columns)), list(columns), fontsize=8)
    axis.set_yticks(np.arange(len(labels)), labels, fontsize=8)
    for row in range(values.shape[0]):
        for column in range(values.shape[1]):
            axis.text(
                column,
                row,
                f"{values[row, column]:+.3f}",
                ha="center",
                va="center",
                fontsize=7,
                color=(
                    "white" if abs(values[row, column]) > 0.55 * limit else "#111827"
                ),
            )
    for boundary in (2.5, 10.5):
        axis.axhline(boundary, color="white", linewidth=1.8)
    axis.set_title("Task-score change from 8,192 to 2,048 tokens", weight="bold")
    figure.colorbar(
        image,
        ax=axis,
        fraction=0.035,
        pad=0.025,
        label="Δ task score (2,048 − 8,192)",
    )
    figure.text(
        0.5,
        0.01,
        "Positive values favor the centered 2,048-token crop. Structural variants are omitted because their historical metric requires the 8,192-position indel boundary.",
        ha="center",
        fontsize=8.5,
        color="#475569",
    )
    save(figure, output, "exp586-task-context-deltas")


def af_readouts(
    models: list[Model],
    historical: dict,
    output: Path,
) -> None:
    models = selected(models, "af")
    figure, axes = plt.subplots(
        1, len(models), figsize=(6.4 * len(models), 5.4), sharey=True
    )
    axes = np.atleast_1d(axes)
    methods = (
        ("Natural\ncausal suffix", "llr_acgt_avg"),
        ("Full-vocab\ncausal suffix", "llr_full_vocab_avg"),
        ("Target-only\ntwo-sided", "llr_target_poe"),
    )
    for axis, model in zip(axes, models, strict=True):
        result = model.result
        for context, marker, color in (
            ("context-8192", "o", model.color),
            ("context-2048", "s", COLORS["poe"]),
        ):
            metrics = result["profiles"][context]["allele_frequency"]["scores"]
            axis.plot(
                np.arange(len(methods)),
                [metrics[key]["overall"]["spearman"] for _, key in methods],
                marker=marker,
                linewidth=2.2,
                color=color,
                label=context.removeprefix("context-") + " tokens",
            )
        for rung, linestyle in zip(
            ("022t", "039t", "056t"), (":", "--", "-."), strict=True
        ):
            score = historical[rung]["metrics"]["100000"]["llr_acgt_avg"]["spearman"]
            axis.axhline(
                score,
                color=COLORS["dense"],
                linestyle=linestyle,
                linewidth=1,
                alpha=0.65,
                label=DENSE_LABELS[rung] if axis is axes[0] else None,
            )
        legacy = historical["022t"]["historical_10k"]
        for label, style in (("PlantCAD2-Small", ":"), ("PlantCAD2-Large", "--")):
            axis.axhline(
                legacy[label]["spearman"],
                color="#B45309",
                linestyle=style,
                linewidth=1,
                alpha=0.6,
                label=f"{label} (legacy 10k)" if axis is axes[0] else None,
            )
        axis.set_xticks(np.arange(len(methods)), [label for label, _ in methods])
        axis.set_title(model.label, weight="bold")
        axis.grid(axis="y", alpha=0.2)
        axis.set_axisbelow(True)
    axes[0].set_ylabel("Spearman correlation with maize AF")
    axes[0].legend(frameon=False, fontsize=8, ncol=2)
    for axis in axes[1:]:
        axis.legend(frameon=False, fontsize=8)
    figure.suptitle(
        "Allele-frequency readout and context sensitivity", fontsize=15, weight="bold"
    )
    figure.text(
        0.5,
        0.01,
        "All model values use the fixed 94,075-variant split; dense reference lines are prior 8,192-token results on the same split.",
        ha="center",
        fontsize=8.5,
        color="#475569",
    )
    save(figure, output, "exp586-af-readouts")


def probe_value(result: dict, profile: str, key: str) -> tuple[float, list[float]]:
    value = result[profile]["metrics"][key]["overall"]["probe"]
    return value["value"], value["ci95"]


def probe_readouts(
    models: list[Model],
    historical_probe: dict,
    output: Path,
) -> None:
    models = selected(models, "probes")
    probe_results = {
        model.key: {
            profile: load(model.directory / profile / "probes/result.json")
            for profile in ("context-8192", "context-2048")
        }
        for model in models
    }
    figure, axes = plt.subplots(1, 2, figsize=(13.2, 5.8), sharey=True)
    keys = (
        ("Whole\naveraged", "whole_window/strand_average"),
        ("Whole\ndirectional", "whole_window/directional"),
        ("Variant\naveraged", "variant_token/strand_average"),
        ("Variant\ndirectional", "variant_token/directional"),
    )
    x = np.arange(len(keys))
    for axis, profile in zip(axes, ("context-8192", "context-2048"), strict=True):
        offsets = np.linspace(-0.09, 0.09, len(models))
        for model, offset in zip(models, offsets, strict=True):
            values, lower, upper = [], [], []
            for _, key in keys:
                value, interval = probe_value(probe_results[model.key], profile, key)
                values.append(value)
                lower.append(value - interval[0])
                upper.append(interval[1] - value)
            axis.errorbar(
                x + offset,
                values,
                yerr=np.asarray([lower, upper]),
                marker="o",
                capsize=3,
                linewidth=1.8,
                color=model.color,
                label=model.label,
            )
        if profile == "context-8192":
            for rung, style in zip(
                ("022t", "039t", "056t"), (":", "--", "-."), strict=True
            ):
                reference = historical_probe["validation"][rung]
                axis.plot(
                    [x[0], x[2]],
                    [reference["whole_window"], reference["variant_token"]],
                    color=COLORS["dense"],
                    linestyle=style,
                    marker=".",
                    alpha=0.65,
                    label=DENSE_LABELS[rung],
                )
        axis.set_xticks(x, [label for label, _ in keys])
        axis.set_title(profile.removeprefix("context-") + " tokens", weight="bold")
        axis.grid(axis="y", alpha=0.2)
        axis.set_axisbelow(True)
    axes[0].set_ylabel("Held-out Spearman correlation with maize AF")
    axes[0].legend(frameon=False, fontsize=8, ncol=2)
    axes[1].legend(frameon=False, fontsize=8)
    figure.suptitle(
        "Frozen-embedding probes: strand averaging vs directional features",
        fontsize=15,
        weight="bold",
    )
    figure.text(
        0.5,
        0.01,
        "Points show the fixed held-out split; error bars are paired genomic-block bootstrap 95% intervals.",
        ha="center",
        fontsize=8.5,
        color="#475569",
    )
    save(figure, output, "exp586-probe-readouts")


def intrinsic_methods(
    models: list[Model],
    output: Path,
) -> None:
    models = selected(models, "methods")
    figure, axes = plt.subplots(
        1, len(models), figsize=(6.25 * len(models), 5.2), sharey=False
    )
    axes = np.atleast_1d(axes)
    methods = (
        ("Forward", "left_test", "#0F766E"),
        ("Reverse complement", "right_test", "#EA580C"),
        ("Equal two-sided", "poe_equal_test", COLORS["poe"]),
    )
    for axis, model in zip(axes, models, strict=True):
        report = model.method
        assert report is not None
        sweep = report["intrinsic"]["context_sweep"]
        contexts = sorted(map(int, sweep))
        for label, key, color in methods:
            axis.plot(
                contexts,
                [sweep[str(context)][key]["nll"] for context in contexts],
                marker="o",
                linewidth=2,
                color=color,
                label=label,
            )
        axis.axhline(
            np.log(4),
            color="#64748B",
            linestyle=":",
            linewidth=1.3,
            label="Uniform-base chance",
        )
        axis.set_xscale("log", base=2)
        axis.set_xticks(contexts, [f"{value:,}" for value in contexts])
        axis.set_xlabel("One-sided context (bases)")
        axis.set_title(model.label, weight="bold")
        axis.grid(alpha=0.2)
    axes[0].set_ylabel("Held-out nucleotide NLL (lower is better)")
    axes[-1].legend(frameon=False, fontsize=8)
    figure.suptitle(
        "Task-independent bidirectional inference validation",
        fontsize=15,
        weight="bold",
    )
    figure.text(
        0.5,
        0.01,
        "The sweep is independent of PlantCAD2 task labels; both orientations from a source window stay in the same split.",
        ha="center",
        fontsize=8.5,
        color="#475569",
    )
    save(figure, output, "exp586-intrinsic-methods")


def prompt_methods(
    models: list[Model],
    output: Path,
) -> None:
    models = selected(models, "methods")
    figure, axes = plt.subplots(
        1, len(models), figsize=(6.25 * len(models), 4.8), sharex=True
    )
    axes = np.atleast_1d(axes)
    labels = ("Forward", "Reverse comp.", "Two-sided PoE", "Rotated", "Sandwich")
    colors = ("#0F766E", "#EA580C", COLORS["poe"], "#0284C7", "#BE123C")
    for axis, model in zip(axes, models, strict=True):
        report = model.method
        assert report is not None
        intrinsic = report["intrinsic"]
        context = intrinsic["context_sweep"]["2048"]
        prompts = intrinsic["prompt_methods_2048"]
        values = (
            context["left_test"]["nll"],
            context["right_test"]["nll"],
            context["poe_equal_test"]["nll"],
            prompts["rotated"]["nll"],
            prompts["sandwich"]["nll"],
        )
        y = np.arange(len(labels))
        axis.barh(y, values, color=colors, alpha=0.9)
        axis.set_yticks(y, labels)
        axis.invert_yaxis()
        axis.set_title(model.label, weight="bold")
        axis.grid(axis="x", alpha=0.2)
        axis.set_axisbelow(True)
        axis.axvline(np.log(4), color="#64748B", linestyle=":", linewidth=1.3, zorder=0)
        for row, value in enumerate(values):
            axis.text(value + 0.035, row, f"{value:.3f}", va="center", fontsize=8)
    axes[0].set_xlim(0.95, max(axis.get_xlim()[1] for axis in axes) + 0.25)
    for axis in axes:
        axis.set_xlabel("Held-out nucleotide NLL (lower is better)")
    figure.suptitle(
        "Inference-only bidirectional prompt alternatives at 2,048 bases",
        fontsize=15,
        weight="bold",
    )
    figure.subplots_adjust(bottom=0.2)
    figure.text(
        0.5,
        0.025,
        "The dotted line marks uniform-base chance. Equal two-sided scores use separate forward and reverse-complement passes; rotated and sandwich prompts use one causal pass.",
        ha="center",
        fontsize=8.5,
        color="#475569",
    )
    save(figure, output, "exp586-prompt-methods")


def create_report(
    catalog: Path,
    historical: Path,
    output: Path,
) -> None:
    models = load_catalog(catalog)
    history = load(historical / "exp472-lr5e4-full-coreweave-20260831.json")
    af_history = {
        rung: load(historical / f"plantcad2-maize-af-{rung}-20260904-v1.json")
        for rung in ("022t", "039t", "056t")
    }
    model_overview(models, history, output)
    task_heatmap(models, history, output)
    task_context_deltas(models, output)
    af_readouts(models, af_history, output)
    probe_models = selected(models, "probes")
    probe_paths = [
        model.directory / profile / "probes/result.json"
        for model in probe_models
        for profile in ("context-8192", "context-2048")
    ]
    present = [path.exists() for path in probe_paths]
    if any(present) and not all(present):
        raise ValueError("Probe results must be either complete or absent")
    if all(present):
        probe_history = load(
            historical / "exp472-lr5e4-maize-af-probe-validation-20260904.json"
        )
        probe_readouts(models, probe_history, output)
    intrinsic_methods(models, output)
    prompt_methods(models, output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--historical", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    create_report(**vars(parser.parse_args()))


if __name__ == "__main__":
    main()
