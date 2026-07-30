import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "instance", "transit_verify.sqlite3")

# Anomaly aggregation: count by vehiclePlate + terminalZone +
# routeSegment + violationType within a rolling window.
ANOMALY_THRESHOLD = 5
ANOMALY_WINDOW_MINUTES = 15

# Spam filter: volume cap by vehiclePlate + violationType within a
# rolling window, independent of the anomaly threshold above.
SPAM_CEILING = 20
SPAM_WINDOW_MINUTES = 5
