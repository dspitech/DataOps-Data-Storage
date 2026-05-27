SELECT
    source_file,
    message
FROM stg_blob_files
WHERE message IS NOT NULL
