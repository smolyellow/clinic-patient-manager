CREATE TABLE IF NOT EXISTS patients (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  citizen BOOLEAN,
  iden_type TEXT NOT NULL,
  iden_info TEXT NOT NULL,
  birthdate DATE,
  gender BOOLEAN,
  married BOOLEAN,
  phone_number TEXT,
  UNIQUE(name, iden_type, iden_info)
);

CREATE TABLE IF NOT EXISTS medical_history_and_medication(
  patient_id INTEGER PRIMARY KEY,
  mhnm_info TEXT,
  FOREIGN KEY (patient_id) REFERENCES patients(id)
);

CREATE TABLE IF NOT EXISTS allergy(
  patient_id INTEGER PRIMARY KEY,
  allergy TEXT,
  FOREIGN KEY (patient_id) REFERENCES patients(id)
);

CREATE TABLE IF NOT EXISTS symptoms_log(
  patient_id INTEGER PRIMARY KEY,
  log TEXT,
  FOREIGN KEY (patient_id) REFERENCES patients(id)
);

CREATE TABLE IF NOT EXISTS visits(
  id INTEGER PRIMARY KEY,
  patient_id INTEGER,
  visit_date DATE,
  prescription_info TEXT,
  FOREIGN KEY (patient_id) REFERENCES patients(id)
);

CREATE TABLE IF NOT EXISTS liquid_medicine (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  UNIQUE(name)
);

CREATE TABLE IF NOT EXISTS liquid_medicine_usage (
  visit_id INTEGER,
  liquid_medicine_id INTEGER,
  usage_ml INTEGER,
  FOREIGN KEY (visit_id) REFERENCES visits(id),
  FOREIGN KEY (liquid_medicine_id) REFERENCES liquid_medicine (id)
);
