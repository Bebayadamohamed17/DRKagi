import requests
import time
from datetime import datetime

class CVELookup:
    def __init__(self):
        self.base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.last_request_time = 0
        self.request_interval = 6.0  # NVD limit without API key is roughly 5 per 30s (~6s/req)

    def _rate_limit(self):
        """Ensures we don't hit NVD rate limits."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.request_interval:
            time.sleep(self.request_interval - elapsed)
        self.last_request_time = time.time()

    def search_cve(self, service_name, version):
        """
        Searches for CVEs for a specific service and version.
        Returns a list of dictionaries with CVE ID, Severity, and Description.
        """
        if not version or not service_name or service_name.lower() == "unknown":
            return []

        # Clean up version string (remove extra text like '(Ubuntu)', etc.)
        clean_version = version.split(' ')[0]
        keyword = f"{service_name} {clean_version}"
        
        params = {
            'keywordSearch': keyword,
            'resultsPerPage': 5  # Limit results to keep it fast/relevant
        }

        try:
            self._rate_limit()
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = []
                
                for item in data.get('vulnerabilities', []):
                    cve = item.get('cve', {})
                    cve_id = cve.get('id')
                    try:
                        # Extract description
                        descriptions = cve.get('descriptions', [])
                        desc_text = descriptions[0].get('value') if descriptions else "No description"
                        
                        # Extract metrics (severity) - V3.1 preferred, then V3.0, then V2
                        metrics = cve.get('metrics', {})
                        severity = "UNKNOWN"
                        
                        if 'cvssMetricV31' in metrics:
                            severity = metrics['cvssMetricV31'][0]['cvssData']['baseSeverity']
                        elif 'cvssMetricV30' in metrics:
                            severity = metrics['cvssMetricV30'][0]['cvssData']['baseSeverity']
                        elif 'cvssMetricV2' in metrics:
                            severity = metrics['cvssMetricV2'][0]['baseSeverity']
                            
                        vulnerabilities.append({
                            "id": cve_id,
                            "severity": severity,
                            "description": desc_text[:200] + "..." if len(desc_text) > 200 else desc_text
                        })
                    except Exception as e:
                        print(f"[debug] Error parsing CVE {cve_id}: {e}")
                        continue
                        
                return vulnerabilities
            else:
                print(f"[!] NVD API Error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"[!] CVE Lookup Error: {e}")
            return []
