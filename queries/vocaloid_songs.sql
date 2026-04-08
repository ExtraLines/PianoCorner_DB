WITH vocaloid_songs AS (
    SELECT song_id, original_name, english_name
    FROM songs
    WHERE genre = 'Vocaloid'
),
voicebank_assignments AS (
    SELECT song_id, artist_id
    FROM song_to_artist
    WHERE role = 'Voicebank'
)
SELECT 
    vs.original_name AS song_original_name,
    vs.english_name AS song_english_name,
    a.original_name AS voicebank_name
FROM vocaloid_songs vs
LEFT JOIN voicebank_assignments va 
    ON vs.song_id = va.song_id
LEFT JOIN artists a 
    ON va.artist_id = a.artist_id
ORDER BY vs.english_name ASC;