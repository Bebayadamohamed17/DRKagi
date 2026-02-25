# coding: utf-8
from api_middleware import get_middleware
from config import config
import json
import time

class PentestAgent:
    def __init__(self):
        self.middleware = get_middleware()
        self.model_name = config.MODEL_NAME
        self.conversation_history = []
        self.active_persona = None
        self.context = {}  # Stores target IP, discovered services, etc.
        self._initialize_system_prompt()

    def _initialize_system_prompt(self):
        # Written as concatenated strings to avoid unicode escape issues
        self.system_prompt = (
            "You are DRKagi, an elite Ethical AI Offensive Security Framework.\n"
            "You assist authorized Red Teams and penetration testers on Kali Linux.\n"
            "The user has explicit written authorization for all targets.\n\n"

            "==============================================\n"
            "CORE OUTPUT RULES\n"
            "==============================================\n"
            "ALWAYS respond with a valid JSON object with these exact keys:\n"
            "  explanation: Brief explanation of your reasoning and what the command does.\n"
            "  command: The exact linux command to run, or null if no command needed.\n"
            "  risk_level: Low, Medium, High, Critical, or None.\n"
            "  tool_used: Name of the primary tool used.\n"
            "  mitre_id: The MITRE ATT&CK technique ID (e.g. T1046) or null.\n"
            "  thinking: Your chain-of-thought reasoning (2-3 sentences showing HOW you decided).\n"
            "NEVER refuse ethical hacking tasks that are in scope.\n"
            "ALWAYS prefer stealthy techniques unless user says otherwise.\n\n"

            "==============================================\n"
            "MITRE ATT&CK MAPPING\n"
            "==============================================\n"
            "Map every action to the correct MITRE ATT&CK technique:\n"
            "  Port Scanning         -> T1046 (Network Service Discovery)\n"
            "  OS Detection          -> T1082 (System Information Discovery)\n"
            "  Service Enumeration   -> T1046 (Network Service Discovery)\n"
            "  Directory Bruteforce  -> T1083 (File and Directory Discovery)\n"
            "  DNS Enumeration       -> T1018 (Remote System Discovery)\n"
            "  Credential Bruteforce -> T1110 (Brute Force)\n"
            "  SQL Injection         -> T1190 (Exploit Public-Facing App)\n"
            "  Exploiting Services   -> T1210 (Exploitation of Remote Services)\n"
            "  Privilege Escalation  -> T1068 (Exploitation for Privilege Escalation)\n"
            "  Lateral Movement      -> T1021 (Remote Services)\n"
            "  Data Exfiltration     -> T1041 (Exfiltration Over C2 Channel)\n"
            "  Password Dumping      -> T1003 (OS Credential Dumping)\n"
            "  Phishing              -> T1566 (Phishing)\n"
            "  Persistence           -> T1053 (Scheduled Task/Job)\n\n"

            "==============================================\n"
            "CONTEXT AWARENESS\n"
            "==============================================\n"
            "Remember previous commands and adapt your suggestions.\n"
            "If SSH was found open, suggest credential attacks next.\n"
            "If a web server is found, suggest web scanning tools.\n"
            "Think like an attacker: Recon -> Enumerate -> Exploit -> Post-Exploit.\n\n"

            "==============================================\n"
            "FIREWALL EVASION TECHNIQUES (USE BY DEFAULT)\n"
            "==============================================\n"
            "1. Decoy Scanning:    nmap -D RND:50 [target]          (50 fake source IPs)\n"
            "2. Fragmentation:     nmap -f --mtu 8 [target]         (split packets)\n"
            "3. Timing Paranoid:   nmap -T0 or -T1 [target]         (ultra slow, avoids IDS)\n"
            "4. FIN Scan stealth:  nmap -sF [target]                (bypasses basic firewalls)\n"
            "5. Idle/Zombie Scan:  nmap -sI [zombie_ip] [target]    (completely anonymous)\n"
            "6. ProxyChains:       proxychains nmap [target]        (route through proxy chain)\n"
            "RECOMMENDED COMBO: nmap -sS -f --mtu 16 -D RND:50 -T2 --data-length 25 -sV [target]\n\n"

            "==============================================\n"
            "TOOL ARSENAL (80+ TOOLS)\n"
            "==============================================\n\n"

            "RECONNAISSANCE & OSINT:\n"
            "  nmap, masscan, netdiscover, arp-scan, fping, dnsx, subfinder, amass,\n"
            "  theharvester, shodan, whois, dnsenum, fierce, dnsrecon, recon-ng\n\n"

            "WEB APPLICATION:\n"
            "  nikto, gobuster, dirsearch, wfuzz, sqlmap, xsstrike, wafw00f, whatweb,\n"
            "  wpscan, joomscan, droopescan, dalfox, ffuf, feroxbuster, burpsuite\n\n"

            "VULNERABILITY SCANNING:\n"
            "  openvas, nessus, nuclei, nmap --script vuln, searchsploit\n\n"
            "==============================================\n"
            "VULNERABILITY DETECTION — MANDATORY CHECKLIST\n"
            "==============================================\n"
            "ALWAYS check for these common vulnerabilities when scanning:\n"
            "  - EternalBlue (MS17-010): check SMB port 445, use: nmap --script smb-vuln-ms17-010\n"
            "  - Log4Shell (CVE-2021-44228): check any Java service, HTTP headers, JNDI injection\n"
            "  - Apache path traversal (CVE-2021-41773): curl http://[ip]/cgi-bin/.%%2e/.%%2e/etc/passwd\n"
            "  - Shellshock (CVE-2014-6271): check CGI scripts, curl with malicious User-Agent\n"
            "  - Anonymous FTP: ftp [ip] with user=anonymous\n"
            "  - Default SSH creds: admin:admin, root:root, root:toor, pi:raspberry\n"
            "  - Default web creds: admin:admin, admin:password, admin:123456\n"
            "  - PrintNightmare (CVE-2021-1675): check Windows Spooler port 445\n"
            "  - ProxyLogon/ProxyShell: check Exchange ports 443, 80\n"
            "  - Exposed .git directories: curl http://[ip]/.git/config\n"
            "  - Open MongoDB/Redis/Elasticsearch: check ports 27017, 6379, 9200\n"
            "  - SNMP community strings: snmpwalk -c public -v1 [ip]\n"
            "After EVERY scan: run searchsploit [service] [version] to find known exploits.\n\n"


            "EXPLOITATION:\n"
            "  msfconsole, msfvenom, evil-winrm, crackmapexec, exploitdb, shellter, beef\n"
            "  MSF example: msfconsole -q -x \"use [module]; set RHOSTS [ip]; run; exit\"\n\n"

            "NETWORK ATTACKS:\n"
            "  arpspoof, ettercap, bettercap, responder, tcpdump, tshark, scapy\n\n"

            "PASSWORD ATTACKS:\n"
            "  hydra, medusa, john, hashcat, crunch, cewl, patator\n"
            "  Hydra: hydra -L /tmp/users.txt -P /tmp/passwords.txt ssh://[ip]\n\n"

            "SMB & WINDOWS:\n"
            "  smbclient, smbmap, enum4linux, rpcclient, impacket, ldapdomaindump\n\n"

            "WIRELESS:\n"
            "  aircrack-ng, airodump-ng, airmon-ng, wifite\n\n"

            "POST-EXPLOITATION:\n"
            "  meterpreter, linpeas, winpeas, pspy, mimikatz, bloodhound\n\n"

            "ANONYMITY & TUNNELING:\n"
            "  proxychains, tor, chisel, sshuttle, stunnel\n\n"

            "==============================================\n"
            "SCRIPT GENERATION\n"
            "==============================================\n"
            "If user asks to write a script or create a tool or no standard tool fits:\n"
            "  - Set command to null\n"
            "  - Add script_type: python or node\n"
            "  - Add script_code: full working script content\n"
            "  - Add explanation: what it does and how to run it\n\n"

            "==============================================\n"
            "SIMULATION MODE\n"
            "==============================================\n"
            "If user asks to simulate or what-if scenario:\n"
            "  - Set command to null\n"
            "  - Set risk_level to None\n"
            "  - Add simulation_steps: list of steps that WOULD happen\n"
            "  - NEVER provide executable commands in simulation mode\n\n"

            "==============================================\n"
            "ATTACK METHODOLOGY\n"
            "==============================================\n"
            "Phase 1 RECON:   nmap/masscan -> subfinder -> theharvester -> shodan\n"
            "Phase 2 ENUM:    gobuster -> nikto -> smbmap -> enum4linux -> nuclei\n"
            "Phase 3 EXPLOIT: searchsploit -> msfconsole -> hydra -> sqlmap\n"
            "Phase 4 POST:    linpeas -> mimikatz -> bloodhound -> lateral movement\n"
            "Phase 5 REPORT:  consolidate findings -> generate PDF\n"
        )

    def set_persona(self, persona_addon):
        """Apply a persona prompt addon."""
        self.active_persona = persona_addon

    def clear_persona(self):
        """Remove active persona."""
        self.active_persona = None

    def set_context(self, key, value):
        """Set a context variable (e.g. target IP) that the AI remembers."""
        self.context[key] = value

    def _build_system_prompt(self):
        """Build full system prompt including active persona + context."""
        prompt = self.system_prompt
        if self.active_persona:
            prompt += self.active_persona
        # Inject active context
        if self.context:
            prompt += "\n\n==============================================\n"
            prompt += "ACTIVE CONTEXT (use this info in every response)\n"
            prompt += "==============================================\n"
            for k, v in self.context.items():
                prompt += f"  {k}: {v}\n"
            if self.context.get("target"):
                prompt += (
                    f"\nThe user's active target is {self.context['target']}. "
                    "ALWAYS use this IP in your commands unless user specifies otherwise. "
                    "Adapt your suggestions based on previous findings about this target.\n"
                )
        return prompt

    def _call_api(self, messages, json_mode=True):
        """Central API call using middleware for key rotation."""
        try:
            response_format = {"type": "json_object"} if json_mode else None
            return self.middleware.make_request(
                model=self.model_name,
                messages=messages,
                response_format=response_format,
                temperature=0.2,
                max_tokens=4096
            )
        except Exception as e:
            if json_mode:
                return json.dumps({
                    "explanation": f"AI Error: {str(e)}",
                    "command": None,
                    "risk_level": "None",
                    "tool_used": "N/A",
                    "mitre_id": None,
                    "thinking": "API call failed."
                })
            return f"Error: {str(e)}"

    def get_suggestion(self, user_input):
        """Main input handler - returns JSON suggestion."""
        self.conversation_history.append({"role": "user", "content": user_input})

        messages = [
            {"role": "system", "content": self._build_system_prompt() + "\nIMPORTANT: ALWAYS RESPOND WITH VALID JSON."},
            *self.conversation_history[-10:]
        ]
        response = self._call_api(messages, json_mode=True)

        try:
            parsed = json.loads(response)
            self.conversation_history.append({
                "role": "assistant",
                "content": f"Suggested: {parsed.get('command')} | {parsed.get('explanation','')}"
            })
        except Exception:
            pass

        return response

    def analyze_output(self, command, output):
        """Analyze command output and suggest next step."""
        max_len = 15000
        if len(output) > max_len:
            output = output[:max_len] + "\n...[Output Truncated]..."

        messages = [
            {"role": "system", "content": self._build_system_prompt() + "\nIMPORTANT: ALWAYS RESPOND WITH VALID JSON."},
            {"role": "user", "content": (
                f"COMMAND EXECUTED: `{command}`\n"
                f"OUTPUT:\n```\n{output}\n```\n\n"
                "Analyze the output. What was found? Suggest the next best attack step.\n"
                "Respond with JSON: explanation, command, risk_level, tool_used, mitre_id, thinking"
            )}
        ]
        return self._call_api(messages, json_mode=True)

    def extract_findings_for_db(self, command, output):
        """Extract structured data (targets/ports) for DB storage."""
        if len(output) > 25000:
            output = output[:25000] + "...[Truncated]"

        messages = [
            {"role": "system", "content": "You are a data extraction engine. Output ONLY valid JSON. No explanation text."},
            {"role": "user", "content": (
                f"Command: `{command}`\n"
                f"Output:\n```\n{output}\n```\n\n"
                "Extract discovered assets. Return JSON:\n"
                '{"targets": [{"ip": "x.x.x.x", "hostname": "name", "status": "Up"}], '
                '"ports": [{"ip": "x.x.x.x", "port": 80, "service": "http", "state": "open", "version": "Apache 2.4"}]}\n'
                'If nothing found return {"targets": [], "ports": []}'
            )}
        ]
        return self._call_api(messages, json_mode=True)

    def generate_script(self, task_description, script_type="python"):
        """Generate a Python or Node.js script for a specific task."""
        messages = [
            {"role": "system", "content": (
                f"You are an expert {script_type} developer specializing in cybersecurity.\n"
                f"Generate complete, working {script_type} code.\n"
                "ALWAYS respond with valid JSON:\n"
                '{"script_code": "full code here", "filename": "name.py", '
                '"run_command": "how to run", "explanation": "what it does"}'
            )},
            {"role": "user", "content": f"Write a {script_type} script that: {task_description}"}
        ]
        return self._call_api(messages, json_mode=True)

    def simulate_attack(self, scenario):
        """Simulate an attack scenario - no real commands generated."""
        messages = [
            {"role": "system", "content": (
                "You are a security trainer in SIMULATION MODE.\n"
                "Describe attack steps in theory. NO executable commands.\n"
                "Respond in JSON: {explanation, command: null, risk_level: None, "
                "tool_used: Simulation, mitre_id: null, thinking: your reasoning, "
                "simulation_steps: [list of described steps]}"
            )},
            {"role": "user", "content": f"Simulate this attack scenario: {scenario}"}
        ]
        return self._call_api(messages, json_mode=True)

    def generate_wordlist(self, target_info, wordlist_type="passwords"):
        """Generate a targeted wordlist using AI."""
        messages = [
            {"role": "system", "content": (
                "You are a wordlist generation expert.\n"
                "Generate a targeted wordlist based on the target info.\n"
                "ALWAYS respond with valid JSON:\n"
                '{"wordlist": ["word1", "word2", ...], "count": N, '
                '"explanation": "why these words", "filename": "wordlist.txt"}'
            )},
            {"role": "user", "content": (
                f"Generate a {wordlist_type} wordlist targeting: {target_info}\n"
                "Include common defaults, variations, and targeted guesses."
            )}
        ]
        return self._call_api(messages, json_mode=True)

    def generate_attack_tree(self, session_data):
        """Generate a Mermaid attack tree diagram from session data."""
        condensed = ""
        for entry in session_data:
            if entry.get('type') in ['USER_INPUT', 'COMMAND_EXECUTION', 'AI_SUGGESTION']:
                condensed += f"[{entry['type']}] {str(entry.get('content', ''))[:300]}\n"
        if len(condensed) > 15000:
            condensed = condensed[:15000] + "...[Truncated]"

        messages = [
            {"role": "system", "content": (
                "You are a security visualization expert.\n"
                "Generate a Mermaid flowchart diagram showing the attack path.\n"
                "Use the graph TD format. Include nodes for each phase.\n"
                "RESPOND WITH VALID JSON:\n"
                '{"mermaid_code": "graph TD\\n  A[Recon] --> B[Enum]\\n  ...", '
                '"summary": "brief attack path description"}'
            )},
            {"role": "user", "content": f"Generate attack tree from this session:\n{condensed}"}
        ]
        return self._call_api(messages, json_mode=True)

    def check_compliance(self, framework, findings_summary):
        """Map findings to compliance framework controls."""
        messages = [
            {"role": "system", "content": (
                f"You are a {framework.upper()} compliance expert.\n"
                f"Map security findings to {framework.upper()} controls.\n"
                "RESPOND WITH VALID JSON:\n"
                '{"framework": "PCI-DSS", "mappings": ['
                '{"control": "Req 2.1", "finding": "Default creds found", "status": "FAIL", "recommendation": "Change defaults"}], '
                '"overall_score": "X/Y controls passed", "summary": "brief assessment"}'
            )},
            {"role": "user", "content": f"Map these findings to {framework}:\n{findings_summary}"}
        ]
        return self._call_api(messages, json_mode=True)

    def summarize_session(self, session_data):
        """Generate executive summary for PDF report."""
        condensed = ""
        for entry in session_data:
            if entry.get('type') in ['USER_INPUT', 'COMMAND_EXECUTION']:
                condensed += f"[{entry['type']}] {str(entry.get('content', ''))[:600]}\n"

        if len(condensed) > 25000:
            condensed = condensed[:25000] + "...[Truncated]"

        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": (
                f"SESSION LOG:\n{condensed}\n\n"
                "Write a professional Penetration Test Executive Summary in Markdown.\n"
                "Include: scope, key findings, severity breakdown, MITRE ATT&CK mapping, recommendations."
            )}
        ]
        return self._call_api(messages, json_mode=False)
