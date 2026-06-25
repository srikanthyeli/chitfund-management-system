import csv
from io import StringIO
from typing import List, Dict, Any

class ReportExportService:
    def __init__(self):
        pass

    def export_to_csv(self, headers: List[str], data: List[Dict[str, Any]]) -> str:
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        return output.getvalue()
