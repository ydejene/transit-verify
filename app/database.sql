-- Reference data
CREATE TABLE IF NOT EXISTS zones (
    zoneId INTEGER PRIMARY KEY AUTOINCREMENT,
    assignedZoneName TEXT NOT NULL,
    physicalHubLocation TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS route_segments (
    routeId INTEGER PRIMARY KEY AUTOINCREMENT,
    routeCode TEXT NOT NULL,
    routeName TEXT NOT NULL,
    zoneId INTEGER NOT NULL,
    FOREIGN KEY (zoneId) REFERENCES zones (zoneId)
);

CREATE TABLE IF NOT EXISTS violation_types (
    violationId INTEGER PRIMARY KEY AUTOINCREMENT,
    violationName TEXT NOT NULL,
    description TEXT
);

-- Auth
CREATE TABLE IF NOT EXISTS users (
    userId INTEGER PRIMARY KEY AUTOINCREMENT,
    fullName TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    passwordHash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('TerminalManager', 'Supervisor', 'Officer')),
    assignedZone TEXT,
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    lastLogin DATETIME
);

-- Core data
CREATE TABLE IF NOT EXISTS anomalies (
    anomalyId INTEGER PRIMARY KEY AUTOINCREMENT,
    vehiclePlate TEXT NOT NULL,
    terminalZone TEXT NOT NULL,
    routeSegment TEXT NOT NULL,
    violationType TEXT NOT NULL,
    reportCount INTEGER NOT NULL,
    windowStart DATETIME NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('Pending', 'Reviewed', 'Resolved')),
    penaltyReceiptRef TEXT DEFAULT '',
    updated_by_user_id INTEGER,
    updated_at DATETIME,
    FOREIGN KEY (updated_by_user_id) REFERENCES users (userId)
);

CREATE TABLE IF NOT EXISTS raw_reports (
    reportId INTEGER PRIMARY KEY AUTOINCREMENT,
    vehiclePlate TEXT NOT NULL,
    terminalZone TEXT NOT NULL,
    routeSegment TEXT NOT NULL,
    violationType TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    anomaly_id INTEGER DEFAULT NULL,
    FOREIGN KEY (anomaly_id) REFERENCES anomalies (anomalyId)
);

-- Audit
CREATE TABLE IF NOT EXISTS spam_log (
    logId INTEGER PRIMARY KEY AUTOINCREMENT,
    vehiclePlate TEXT NOT NULL,
    violationType TEXT NOT NULL,
    terminalZone TEXT NOT NULL,
    routeSegment TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
