BEGIN;

CREATE SCHEMA IF NOT EXISTS soil_monitoring;
SET search_path TO soil_monitoring, public;

CREATE TABLE IF NOT EXISTS dim_experiments (
    experiment_sk BIGSERIAL PRIMARY KEY,
    project_id TEXT,
    experiment_id TEXT,
    experiment_title TEXT,
    start_date DATE,
    expected_end_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dim_sites (
    site_sk BIGSERIAL PRIMARY KEY,
    experiment_sk BIGINT NOT NULL REFERENCES dim_experiments(experiment_sk) ON DELETE CASCADE,
    site_id TEXT,
    field_identifier TEXT,
    gps_lat NUMERIC(9,6),
    gps_lon NUMERIC(9,6),
    soil_type_texture TEXT,
    field_size_ha NUMERIC(12,4),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (experiment_sk, site_id)
);

CREATE TABLE IF NOT EXISTS dim_treatments (
    treatment_sk BIGSERIAL PRIMARY KEY,
    experiment_sk BIGINT NOT NULL REFERENCES dim_experiments(experiment_sk) ON DELETE CASCADE,
    treatment_code TEXT NOT NULL,
    treatment_name TEXT,
    treatment_type TEXT,
    description TEXT,
    is_control BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (experiment_sk, treatment_code)
);

CREATE TABLE IF NOT EXISTS dim_practices (
    practice_sk BIGSERIAL PRIMARY KEY,
    treatment_sk BIGINT NOT NULL REFERENCES dim_treatments(treatment_sk) ON DELETE CASCADE,
    practice_type TEXT,
    practice_name TEXT,
    practice_value TEXT,
    unit TEXT,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dim_plots (
    plot_sk BIGSERIAL PRIMARY KEY,
    site_sk BIGINT NOT NULL REFERENCES dim_sites(site_sk) ON DELETE CASCADE,
    treatment_sk BIGINT NOT NULL REFERENCES dim_treatments(treatment_sk) ON DELETE RESTRICT,
    plot_id TEXT,
    replicate_no INTEGER,
    block_no INTEGER,
    sample_point_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (site_sk, plot_id)
);

CREATE TABLE IF NOT EXISTS dim_sampling_events (
    sample_sk BIGSERIAL PRIMARY KEY,
    site_sk BIGINT NOT NULL REFERENCES dim_sites(site_sk) ON DELETE CASCADE,
    plot_sk BIGINT REFERENCES dim_plots(plot_sk) ON DELETE SET NULL,
    sample_id TEXT NOT NULL UNIQUE,
    layer_id TEXT,
    sampling_date DATE,
    sampling_timepoint TEXT,
    author TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dim_indicators (
    indicator_sk BIGSERIAL PRIMARY KEY,
    indicator_code TEXT NOT NULL UNIQUE,
    indicator_name TEXT NOT NULL,
    default_unit TEXT,
    value_type TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fact_measurements (
    measurement_sk BIGSERIAL PRIMARY KEY,
    sample_sk BIGINT NOT NULL REFERENCES dim_sampling_events(sample_sk) ON DELETE CASCADE,
    indicator_sk BIGINT NOT NULL REFERENCES dim_indicators(indicator_sk) ON DELETE RESTRICT,
    result_domain TEXT,
    measured_value_num NUMERIC(18,6),
    measured_value_text TEXT,
    unit TEXT,
    qa_status TEXT DEFAULT 'raw',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMIT;
