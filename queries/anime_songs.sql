WITH anime_sources AS (
    SELECT source_id, original_title, english_title
    FROM sources
    WHERE type = 'Anime'
)
SELECT 
    s.original_name AS song_original_name,
    s.english_name AS song_english_name,
    ans.original_title AS anime_original_title,
    ans.english_title AS anime_english_title,
    sts.relation
FROM 
    songs s
JOIN 
    song_to_source sts ON s.song_id = sts.song_id
JOIN 
    anime_sources ans ON sts.source_id = ans.source_id
ORDER BY 
    ans.english_title ASC;