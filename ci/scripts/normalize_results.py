from pathlib import Path
import re
import sys
import pandas as pd

RAW_BASE_DIR = Path("analysis/raw")
PROCESSED_DIR = Path("analysis/processed")
OUTPUT_FILE = PROCESSED_DIR / "results_normalized.csv"

SCENARIOS = {
    "c1": {
        "scenario_order": 1,
        "scenario_label": "C1 - Baseline",
        "security_layer": "none",
    },
    "c2": {
        "scenario_order": 2,
        "scenario_label": "C2 - SAST",
        "security_layer": "sast",
    },
    "c3": {
        "scenario_order": 3,
        "scenario_label": "C3 - SAST + SCA",
        "security_layer": "sast_sca",
    },
    "c4": {
        "scenario_order": 4,
        "scenario_label": "C4 - SAST + SCA + DAST",
        "security_layer": "sast_sca_dast",
    },
    "c5": {
        "scenario_order": 5,
        "scenario_label": "C5 - Optimized",
        "security_layer": "optimized",
    },
}

REQUIRED_COLUMNS = [
    "scenario",
    "run_id",
    "run_number",
    "commit_sha",
    "step_name",
    "start_timestamp",
    "end_timestamp",
    "duration_seconds",
    "status",
]

SECURITY_STEPS = {
    "sonarqube_sast",
    "sca_fs",
    "sca_image",
    "sca_total",
    "dast_health_check",
    "dast_zap_baseline",
}

DEPLOY_STEPS = {
    "kubernetes_deploy",
    "kubernetes_smoke_test",
}

def extract_run_index(file_name: str) -> int | None:
    match = re.search(r"_run_(\d+)\.csv$", file_name)
    if not match:
        return None
    return int(match.group(1))

def load_timing_files() -> pd.DataFrame:
    frames = []

    print("NORMALIZACAO DOS RESULTADOS EXPERIMENTAIS")
    print("=" * 80)

    for scenario_key, metadata in SCENARIOS.items():
        timing_dir = RAW_BASE_DIR / scenario_key / "timing"
        files = sorted(timing_dir.glob("*.csv"))

        print(f"\nCenario {scenario_key.upper()}")
        print("-" * 80)
        print(f"Pasta: {timing_dir}")
        print(f"Arquivos encontrados: {len(files)}")

        if len(files) == 0:
            print(f"ERRO: nenhum CSV encontrado para {scenario_key}.")
            sys.exit(1)

        if len(files) < 5:
            print(f"AVISO: {scenario_key} possui menos de 5 execucoes.")

        for file in files:
            df = pd.read_csv(file)

            missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
            if missing_columns:
                print(f"ERRO: {file} nao possui colunas obrigatorias: {missing_columns}")
                sys.exit(1)

            df["duration_seconds"] = pd.to_numeric(df["duration_seconds"], errors="coerce")

            if df["duration_seconds"].isna().any():
                print(f"ERRO: {file} possui duration_seconds invalido.")
                sys.exit(1)

            has_workflow_total = "workflow_total" in df["step_name"].astype(str).values
            if not has_workflow_total:
                print(f"ERRO: {file} nao possui workflow_total.")
                sys.exit(1)

            statuses = sorted(df["status"].astype(str).unique())
            is_valid_execution = statuses == ["success"]

            if not is_valid_execution:
                print(f"AVISO: {file} possui status diferente de success: {statuses}")

            run_index = extract_run_index(file.name)

            df.insert(0, "scenario_key", scenario_key)
            df.insert(1, "scenario_order", metadata["scenario_order"])
            df.insert(2, "scenario_label", metadata["scenario_label"])
            df.insert(3, "security_layer", metadata["security_layer"])
            df.insert(4, "run_index", run_index)
            df.insert(5, "source_file", str(file).replace("\\", "/"))

            df["step_name"] = df["step_name"].astype(str)
            df["status"] = df["status"].astype(str)

            df["is_workflow_total"] = df["step_name"] == "workflow_total"
            df["is_security_step"] = df["step_name"].isin(SECURITY_STEPS)
            df["is_deploy_step"] = df["step_name"].isin(DEPLOY_STEPS)
            df["is_valid_execution"] = is_valid_execution

            frames.append(df)

            workflow_total = df.loc[
                df["step_name"] == "workflow_total",
                "duration_seconds"
            ].tolist()

            print(f"OK: {file.name} | linhas={len(df)} | workflow_total={workflow_total}")

    return pd.concat(frames, ignore_index=True)

def validate_summary(df: pd.DataFrame) -> None:
    print("\nRESUMO DE EXECUCOES VALIDAS POR CENARIO")
    print("=" * 80)

    workflow_df = df[df["is_workflow_total"]].copy()

    summary = (
        workflow_df
        .groupby(["scenario_key", "scenario_label"], as_index=False)
        .agg(
            valid_runs=("run_index", "nunique"),
            mean_workflow_total_seconds=("duration_seconds", "mean"),
            min_workflow_total_seconds=("duration_seconds", "min"),
            max_workflow_total_seconds=("duration_seconds", "max"),
        )
        .sort_values("scenario_key")
    )

    print(summary.to_string(index=False))

    for _, row in summary.iterrows():
        if row["valid_runs"] < 5:
            print(f"AVISO: {row['scenario_key']} possui menos de 5 execucoes validas.")

def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df = load_timing_files()

    comparable_df = df[df["is_valid_execution"]].copy()

    comparable_df = comparable_df.sort_values(
        by=["scenario_order", "run_index", "is_workflow_total", "step_name"],
        ascending=[True, True, True, True],
    )

    comparable_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    validate_summary(comparable_df)

    print("\nArquivo gerado:")
    print(OUTPUT_FILE)
    print(f"Total de linhas no dataset consolidado: {len(comparable_df)}")

if __name__ == "__main__":
    main()
