from __future__ import annotations


def create_breast_cancer_table_sql(table: str) -> str:
    return f"""
    CREATE TABLE IF NOT EXISTS {table} (
        mean_radius double precision,
        mean_texture double precision,
        mean_perimeter double precision,
        mean_area double precision,
        mean_smoothness double precision,
        mean_compactness double precision,
        mean_concavity double precision,
        mean_concave_points double precision,
        mean_symmetry double precision,
        mean_fractal_dimension double precision,
        radius_error double precision,
        texture_error double precision,
        perimeter_error double precision,
        area_error double precision,
        smoothness_error double precision,
        compactness_error double precision,
        concavity_error double precision,
        concave_points_error double precision,
        symmetry_error double precision,
        fractal_dimension_error double precision,
        worst_radius double precision,
        worst_texture double precision,
        worst_perimeter double precision,
        worst_area double precision,
        worst_smoothness double precision,
        worst_compactness double precision,
        worst_concavity double precision,
        worst_concave_points double precision,
        worst_symmetry double precision,
        worst_fractal_dimension double precision,
        target integer,
        ingestion_date date
    )
    """


def create_eval_table_sql(table: str) -> str:
    return f"""
    CREATE TABLE IF NOT EXISTS {table} (
        run_id text,
        accuracy double precision,
        precision_weighted double precision,
        recall_weighted double precision,
        execution_date date
    )
    """
