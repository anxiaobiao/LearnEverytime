-- complain if script is sourced in psql, rather than via CREATE EXTENSION
\echo Use "CREATE EXTENSION array_ext" to load this file. \quit
CREATE FUNCTION array_ext_append(jsonb, numeric) RETURNS jsonb
AS '$libdir/array_ext'
LANGUAGE C IMMUTABLE CALLED ON NULL INPUT;