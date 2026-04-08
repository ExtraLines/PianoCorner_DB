WITH primary_rel AS (
    SELECT 
        song_id, 
        artist_id,
        role 
    FROM 
        song_to_artist 
    WHERE 
        is_primary = TRUE
)
SELECT 
    s.original_name AS song_original_name,
    a.original_name AS artist_name,
    pr.role AS artist_role,
    s.release_date,
    s.genre
FROM 
    songs s
JOIN 
    primary_rel pr ON s.song_id = pr.song_id
JOIN 
    artists a ON pr.artist_id = a.artist_id
ORDER BY
    s.genre ASC, a.english_name ASC;