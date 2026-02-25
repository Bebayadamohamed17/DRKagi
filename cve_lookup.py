"""
CVE Lookup Module — DRKagi v0.4
Provides instant local CVE matching + optional NVD API lookup.
Local DB catches the most common/impactful CVEs without needing internet.
"""
import re
import requests
import time

# ─────────────────────────────────────────────────────────────
# LOCAL CVE PATTERN DATABASE
# Format: (service_regex, version_regex, cve_id, severity, short_desc)
# ─────────────────────────────────────────────────────────────
_LOCAL_CVE_DB = [
    # SMB / Windows
    ("smb|microsoft-ds|netbios", ".*",          "CVE-2017-0144", "CRITICAL", "EternalBlue — RCE via SMBv1 (MS17-010). Exploitable with Metasploit."),
    ("smb|microsoft-ds",         ".*",          "CVE-2021-1675",  "CRITICAL", "PrintNightmare — Windows Print Spooler RCE."),
    ("smb|microsoft-ds",         ".*",          "CVE-2020-0796",  "CRITICAL", "SMBGhost — RCE in SMBv3 compression (Win10/Server 2019)."),
    # Apache
    ("apache|http",              "2\\.4\\.(4[89]|50)",    "CVE-2021-41773",  "CRITICAL", "Apache 2.4.49/50 path traversal & RCE — curl /cgi-bin/.%2e/.%2e/etc/passwd"),
    ("apache|http",              "2\\.[0-4]\\.",          "CVE-2014-6271",   "HIGH",     "Shellshock — Bash RCE via CGI. Test: curl with User-Agent: () { :;}; /bin/bash -i."),
    ("apache|http",              ".*",                    "CVE-2021-44228",  "CRITICAL", "Log4Shell — JNDI injection in Log4j2 (affects Java apps behind Apache)."),
    # OpenSSH
    ("ssh|openssh",              "([1-6]\\.|7\\.[0-6])", "CVE-2018-10933",  "CRITICAL", "libssh auth bypass — connect without password on port 22."),
    ("ssh|openssh",              "([1-7]\\.|8\\.[0-3])", "CVE-2023-38408",  "CRITICAL", "OpenSSH ssh-agent RCE via PKCS#11 provider."),
    # FTP
    ("ftp|vsftpd",               "2\\.3\\.4",            "CVE-2011-2523",   "CRITICAL", "vsftpd 2.3.4 backdoor — connect port 6200 after ':)' login attempt."),
    ("ftp|proftpd",              "1\\.3\\.[35]",         "CVE-2015-3306",   "HIGH",     "ProFTPd mod_copy unauthorized file copy."),
    # Web apps / CMS
    ("http|https|web",           ".*",                   "CVE-2019-0708",   "CRITICAL", "BlueKeep — RDP RCE (Windows 7/Server 2008). Port 3389."),
    ("http|https|web",           ".*",                   "CVE-2021-26084",  "CRITICAL", "Confluence OGNL injection RCE."),
    # MySQL / DB
    ("mysql",                    "5\\.[0-6]\\.",         "CVE-2016-6662",   "CRITICAL", "MySQL 5.x config file injection leading to RCE."),
    ("redis",                    ".*",                   "CVE-2022-0543",   "CRITICAL", "Redis sandbox escape RCE via Lua scripting."),
    ("mongodb",                  ".*",                   "CVE-2013-4650",   "HIGH",     "MongoDB anonymous access — no auth by default in older versions."),
    # Java / JBoss
    ("java|jboss|jmx",          ".*",                   "CVE-2017-12149",  "CRITICAL", "JBoss deserialization RCE — send malicious Java object."),
    ("java|tomcat",              "[1-9]\\.(0\\.[0-4]|[0-8]\\.)", "CVE-2019-0232", "CRITICAL", "Apache Tomcat CGI-BIN RCE on Windows."),
    # Samba
    ("samba",                    "[3-4]\\.",             "CVE-2017-7494",   "CRITICAL", "SambaCry — Samba 3.5.x/4.x RCE via shared library upload. Port 445."),
    # Misc NoSQL + services
    ("elasticsearch",            "[0-6]\\.",             "CVE-2014-3120",   "CRITICAL", "Elasticsearch dynamic scripting RCE — unauthenticated."),
    ("phpmyadmin",               "[4-5]\\.",             "CVE-2016-5734",   "CRITICAL", "phpMyAdmin 4.x preg_replace RCE."),
]


class CVELookup:
    def __init__(self):
        self.base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.last_request_time = 0
        self.request_interval = 6.0

    # ── Local instant match ──────────────────────────────────
    def search_local(self, service_name, version):
        """Instant CVE match from local pattern table — no network needed."""
        results = []
        svc_lower = (service_name or "").lower()
        ver_str   = (version or "").lower()
        for svc_pat, ver_pat, cve_id, severity, desc in _LOCAL_CVE_DB:
            if re.search(svc_pat, svc_lower) and re.search(ver_pat, ver_str):
                results.append({"id": cve_id, "severity": severity, "description": desc})
        return results

    # ── NVD API lookup (slow, optional) ─────────────────────
    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_interval:
            time.sleep(self.request_interval - elapsed)
        self.last_request_time = time.time()

    def search_nvd(self, service_name, version):
        """Query NVD API for additional CVEs."""
        if not version or not service_name or service_name.lower() == "unknown":
            return []
        clean_version = version.split(' ')[0]
        keyword = f"{service_name} {clean_version}"
        params = {'keywordSearch': keyword, 'resultsPerPage': 5}
        try:
            self._rate_limit()
            resp = requests.get(self.base_url, params=params, timeout=8)
            if resp.status_code != 200:
                return []
            data = resp.json()
            results = []
            for item in data.get('vulnerabilities', []):
                cve = item.get('cve', {})
                cve_id = cve.get('id')
                descs = cve.get('descriptions', [])
                desc  = descs[0].get('value', 'No description') if descs else 'No description'
                metrics  = cve.get('metrics', {})
                severity = "UNKNOWN"
                if 'cvssMetricV31' in metrics:
                    severity = metrics['cvssMetricV31'][0]['cvssData']['baseSeverity']
                elif 'cvssMetricV30' in metrics:
                    severity = metrics['cvssMetricV30'][0]['cvssData']['baseSeverity']
                elif 'cvssMetricV2' in metrics:
                    severity = metrics['cvssMetricV2'][0].get('baseSeverity', 'UNKNOWN')
                results.append({"id": cve_id, "severity": severity, "description": desc[:200]})
            return results
        except Exception:
            return []

    # ── Main entry point ─────────────────────────────────────
    def search_cve(self, service_name, version):
        """
        Returns CVEs from local DB first (instant), then NVD if no local match.
        Prioritizes local matches — fast, accurate for common CVEs.
        """
        local = self.search_local(service_name, version)
        if local:
            return local  # Local match found — no need for slow API
        # Fallback to NVD (only if no local match)
        return self.search_nvd(service_name, version)
