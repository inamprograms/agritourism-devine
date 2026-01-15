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
