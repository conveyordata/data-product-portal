-- Example SQLMesh model
-- Replace this with your own models

MODEL (
  name {{ cookiecutter.project_name }}.example_model,
  kind FULL,
  description 'An example model created by the data product portal'
);

SELECT
  1 as id,
  'example' as name,
  CURRENT_TIMESTAMP as created_at;
