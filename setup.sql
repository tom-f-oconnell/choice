
/* TODO set owner of these tables to flypush? will this happen by default b/c
 * way we logged in? */

/* TODO just put in namespace called 'choice' or something? would it be
 * problematic, not having this in flypush namespace (or that's in default
 * anyway)? */
/* CREATE SCHEMA choice; */
/* TODO necessary? autoadded to front of search path on create? */
/* SET search_path TO choice,public; */

/* TODO create basic experiment / run / series structure in parent repo, and
 * inherit from those tables here, maybe also tracking based experiments, as an
 * intermediate in the inheritance */

/* TODO dynamically create this from labelling code in analysis?
   just use str? */
CREATE TYPE trajectory_label AS ENUM (
    'good',
    'never_active',
    'inactive_after_shock',
    'no_sample_either_test',
    'no_receive_shock',
    'no_fly',
    'tracker_artifacts',
    'suspicious'
);

CREATE TABLE IF NOT EXISTS shocked (
    id SERIAL PRIMARY KEY,

    /* TODO maybe use surrogate key in target table to avoid composite fk? */
    tracking_pipeline_num smallint NOT NULL,
    run timestamptz(0) NOT NULL,

    test_number smallint NOT NULL,

    trajec_label trajectory_label,
    /* TODO create odor type w/ name + vial conc? */
    shocked_odor text NOT NULL,
    nonshocked_odor text NOT NULL,

    /* TODO derive from room data (but sensor is rig specific?)
    avg_temp
    avg_humidity
    */
    voltage decimal CHECK (voltage >= 0),
    shock_duty_cycle decimal
        CHECK (shock_duty_cycle > 0 AND shock_duty_cycle <= 1),

    time_spent decimal,
    /* TODO other way to indicate parameters for metrics, like debouncing &
     * decision boundary width? (within single row limit of unique constraint?)
       just add metric parameterization to unique constraint?
    */
    decision_bias decimal,
    accuracy decimal,

    /* TODO derive walking speed before being shocked here? or easier to just do
     * in python? */
    avg_speed_pre_shock decimal,
    avg_speed decimal,

    FOREIGN KEY (tracking_pipeline_num, run)
        REFERENCES trajectories (tracking_pipeline_num, run),

    UNIQUE (tracking_pipeline_num, run, test_number)
);

/* TODO inheritance or something else to not duplicate most code for these
 * tables? */
CREATE TABLE IF NOT EXISTS innate (
    id SERIAL PRIMARY KEY,

    /* TODO maybe use surrogate key in target table to avoid composite fk? */
    tracking_pipeline_num smallint NOT NULL,
    run timestamptz(0) NOT NULL,

    test_number smallint NOT NULL,

    trajec_label trajectory_label,
    /* TODO create odor type w/ name + vial conc? */
    odor_a text NOT NULL,
    odor_b text NOT NULL,

    /* TODO derive from room data (but sensor is rig specific?)
    avg_temp
    avg_humidity
    */
    voltage decimal CHECK (voltage >= 0),
    shock_duty_cycle decimal
        CHECK (shock_duty_cycle > 0 AND shock_duty_cycle <= 1),

    time_spent decimal,
    /* TODO other way to indicate parameters for metrics, like debouncing &
     * decision boundary width? (within single row limit of unique constraint?)
       just add metric parameterization to unique constraint?
    */
    decision_bias decimal,
    accuracy decimal,

    /* TODO derive walking speed before being shocked here? or easier to just do
     * in python? */
    avg_speed_pre_shock decimal,
    avg_speed decimal,

    FOREIGN KEY (tracking_pipeline_num, run)
        REFERENCES trajectories (tracking_pipeline_num, run),

    UNIQUE (tracking_pipeline_num, run, test_number)
);

DELETE FROM flypush_tables WHERE table_name in ('shocked', 'innate');

INSERT INTO flypush_tables (table_name, website_visible, website_editable)
    VALUES ('shocked', TRUE, FALSE);

INSERT INTO flypush_tables (table_name, website_visible, website_editable)
    VALUES ('innate', TRUE, FALSE);
