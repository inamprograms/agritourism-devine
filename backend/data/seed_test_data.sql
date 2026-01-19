-- =========================
-- FARMERS
-- =========================
INSERT INTO farmers (id, name, location)
VALUES
  (1, 'Test Farmer One', 'Rural Area A'),
  (2, 'Test Farmer Two', 'Rural Area B');

-- =========================
-- FARMS
-- =========================
INSERT INTO farms (id, farmer_id, farm_type, size_category)
VALUES
  (101, 1, 'dairy', 'small'),
  (102, 1, 'mixed', 'medium'),
  (201, 2, 'crops', 'small');

-- =========================
-- VISITOR
-- =========================
INSERT INTO visitor (experience_id, views, photos, reviews)
VALUES
  (23, 0, '["https://example.com/photo1.jpg"]', '[{"user":"Alice","rating":5,"comment":"Loved it!"}]');
