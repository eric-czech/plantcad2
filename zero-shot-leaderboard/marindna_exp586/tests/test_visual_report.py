import json
from pathlib import Path

from exp586_evals.visual_report import create_report


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


def test_visual_report_writes_reproducible_png_and_svg_assets(tmp_path: Path):
    root = Path(__file__).parents[1]
    historical = root / "historical"
    full = json.loads(
        (historical / "exp472-lr5e4-full-coreweave-20260831.json").read_text()
    )
    source_rows = full["results"]["022t"]["rows"]
    rows = [
        {
            "key": row["key"],
            "category": row["category"],
            "task": row["task"],
            "natural": row["selected_value"],
            "bidirectional_poe": (
                None
                if row["category"] == "Structural variant"
                else row["selected_value"]
            ),
        }
        for row in source_rows
    ]
    group_values = full["groups"]["022t"]
    groups = dict(
        zip(
            (
                "Conservation",
                "Masked motif",
                "Core/non-core",
                "Structural variant",
                "Composite",
            ),
            group_values,
            strict=True,
        )
    )
    af = {
        "scores": {
            key: {"overall": {"spearman": value}}
            for key, value in (
                ("llr_acgt_avg", 0.15),
                ("llr_full_vocab_avg", 0.151),
                ("llr_target_poe", 0.16),
            )
        }
    }
    result = {
        "profiles": {
            "context-8192": {
                "tasks": {"rows": rows, "groups": {"natural": groups}},
                "allele_frequency": af,
            },
            "context-2048": {
                "tasks": {
                    "rows": [
                        row for row in rows if row["category"] != "Structural variant"
                    ],
                    "groups": {"natural": groups},
                },
                "allele_frequency": af,
            },
        }
    }
    probe = {
        "metrics": {
            key: {"overall": {"probe": {"value": 0.18, "ci95": [0.17, 0.19]}}}
            for key in (
                "whole_window/strand_average",
                "whole_window/directional",
                "variant_token/strand_average",
                "variant_token/directional",
            )
        }
    }
    conditions = {}
    for name in ("pretrained", "random", "language_base"):
        directory = tmp_path / name
        write(directory / "result.json", result)
        for profile in ("context-8192", "context-2048"):
            write(directory / profile / "probes/result.json", probe)
        conditions[name] = directory
    method = {
        "intrinsic": {
            "context_sweep": {
                str(context): {
                    "left_test": {"nll": 1.1},
                    "right_test": {"nll": 1.08},
                    "poe_equal_test": {"nll": 1.0},
                }
                for context in (128, 512, 2048, 4095)
            },
            "prompt_methods_2048": {
                "rotated": {"nll": 1.09},
                "sandwich": {"nll": 1.2},
            },
        }
    }
    pretrained_method = tmp_path / "pretrained-method.json"
    random_method = tmp_path / "random-method.json"
    language_base_method = tmp_path / "language-base-method.json"
    write(pretrained_method, method)
    write(random_method, method)
    write(language_base_method, method)
    output = tmp_path / "assets"
    create_report(
        conditions["pretrained"],
        conditions["random"],
        pretrained_method,
        random_method,
        historical,
        output,
        conditions["language_base"],
        language_base_method,
    )
    names = (
        "exp586-model-family-overview",
        "exp586-task-heatmap",
        "exp586-task-context-deltas",
        "exp586-af-readouts",
        "exp586-probe-readouts",
        "exp586-intrinsic-methods",
        "exp586-prompt-methods",
    )
    for name in names:
        for extension in ("png", "svg"):
            assert (output / f"{name}.{extension}").stat().st_size > 1_000

    for directory in conditions.values():
        for profile in ("context-8192", "context-2048"):
            (directory / profile / "probes/result.json").unlink()
    without_probes = tmp_path / "assets-without-probes"
    create_report(
        conditions["pretrained"],
        conditions["random"],
        pretrained_method,
        random_method,
        historical,
        without_probes,
        conditions["language_base"],
        language_base_method,
    )
    assert not (without_probes / "exp586-probe-readouts.png").exists()
    assert (without_probes / "exp586-model-family-overview.png").exists()
