# Transit Verify — Entity Relationship Diagram

SQLite, 7 tables. All primary keys are `INTEGER PRIMARY KEY AUTOINCREMENT`.

## Reference data

**zones**
| Column | Type | Constraints |
|---|---|---|
| zoneId | INTEGER | PK |
| assignedZoneName | TEXT | NOT NULL |
| physicalHubLocation | TEXT | NOT NULL |

**route_segments**
| Column | Type | Constraints |
|---|---|---|
| routeId | INTEGER | PK |
| routeCode | TEXT | NOT NULL |
| routeName | TEXT | NOT NULL |
| zoneId | INTEGER | NOT NULL, FK → zones.zoneId |

**violation_types**
| Column | Type | Constraints |
|---|---|---|
| violationId | INTEGER | PK |
| violationName | TEXT | NOT NULL |
| description | TEXT | |

## Auth

**users**
| Column | Type | Constraints |
|---|---|---|
| userId | INTEGER | PK |
| fullName | TEXT | NOT NULL |
| email | TEXT | NOT NULL, UNIQUE |
| passwordHash | TEXT | NOT NULL |
| role | TEXT | NOT NULL, CHECK IN (TerminalManager, Supervisor, Officer) |
| assignedZone | TEXT | |
| createdAt | DATETIME | DEFAULT CURRENT_TIMESTAMP |
| lastLogin | DATETIME | |

## Core data

**anomalies**
| Column | Type | Constraints |
|---|---|---|
| anomalyId | INTEGER | PK |
| vehiclePlate | TEXT | NOT NULL |
| terminalZone | TEXT | NOT NULL |
| routeSegment | TEXT | NOT NULL |
| violationType | TEXT | NOT NULL |
| reportCount | INTEGER | NOT NULL |
| windowStart | DATETIME | NOT NULL |
| status | TEXT | NOT NULL, CHECK IN (Pending, Reviewed, Resolved) |
| penaltyReceiptRef | TEXT | DEFAULT '' |
| updated_by_user_id | INTEGER | FK → users.userId, nullable |
| updated_at | DATETIME | nullable |

**raw_reports**
| Column | Type | Constraints |
|---|---|---|
| reportId | INTEGER | PK |
| vehiclePlate | TEXT | NOT NULL |
| terminalZone | TEXT | NOT NULL |
| routeSegment | TEXT | NOT NULL |
| violationType | TEXT | NOT NULL |
| timestamp | DATETIME | DEFAULT CURRENT_TIMESTAMP |
| anomaly_id | INTEGER | DEFAULT NULL, FK → anomalies.anomalyId |

## Audit

**spam_log**
| Column | Type | Constraints |
|---|---|---|
| logId | INTEGER | PK |
| vehiclePlate | TEXT | NOT NULL |
| violationType | TEXT | NOT NULL |
| terminalZone | TEXT | NOT NULL |
| routeSegment | TEXT | NOT NULL |
| timestamp | DATETIME | DEFAULT CURRENT_TIMESTAMP |

## Relationships

- `zones` 1—N `route_segments`
- `anomalies` N—1 `users` (via `updated_by_user_id`, optional — unset until first status update)
- `raw_reports` N—1 `anomalies` (via `anomaly_id`, optional — NULL until the report contributes to a threshold)
- `raw_reports.terminalZone` / `routeSegment` / `violationType` reference `zones` / `route_segments` / `violation_types` by name (denormalized text, not enforced FKs) — matches how `anomalies` also stores these as text rather than joining, so a manager's dashboard view never needs a join to read a row
