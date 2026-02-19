# تقرير المشروع الشامل: DRKagi v0.3
## إطار اختبار الاختراق بالذكاء الاصطناعي

---

<div dir="rtl">

**المؤلف:** DRKagi Development Team  
**الإصدار:** 0.3.0  
**التاريخ:** فبراير 2026  
**التصنيف:** أداة أمنية — مرخصة للاختبار المرخص فقط

</div>

---

## 📋 جدول المحتويات

1. [نظرة عامة على المشروع](#1-نظرة-عامة-على-المشروع)
2. [المشكلة والحل](#2-المشكلة-والحل)
3. [المعمارية التقنية](#3-المعمارية-التقنية)
4. [الملفات والوحدات التفصيلية](#4-الملفات-والوحدات-التفصيلية)
5. [ميزات المنتج الكاملة](#5-ميزات-المنتج-الكاملة)
6. [كيفية الاستخدام — شرح تفصيلي](#6-كيفية-الاستخدام--شرح-تفصيلي)
7. [مسار التعلم — من المبتدئ للمتقدم](#7-مسار-التعلم--من-المبتدئ-للمتقدم)
8. [التطوير والتوسيع](#8-التطوير-والتوسيع)
9. [الأمان والأخلاقيات](#9-الأمان-والأخلاقيات)
10. [خطط المستقبل](#10-خطط-المستقبل)

---

## 1. نظرة عامة على المشروع

### ما هو DRKagi؟

**DRKagi** هو إطار اختبار اختراق مدعوم بالذكاء الاصطناعي (AI-powered penetration testing framework)، مصمم لأتمتة عمليات Red Team ومساعدة المختبرين الأمنيين على تنفيذ تقييمات شاملة بكفاءة وسرعة.

بدلاً من تذكر مئات الأوامر، يكفيك أن تكتب بلغتك الطبيعية:
```
DRKagi > scan the target for open services
DRKagi > try to brute force SSH on port 22
DRKagi > what vulnerabilities does this Apache version have?
```

والذكاء الاصطناعي يفهم السياق ويختار الأداة الصحيحة ويكتب الأمر المناسب.

### الفلسفة الأساسية

| المبدأ | التطبيق |
|--------|---------|
| **AI-First** | كل قرار يمر عبر Llama 3.3 70B |
| **Context-Aware** | يتذكر الهدف والنتائج السابقة |
| **Zero-Config** | يعمل بدون إعداد — المفاتيح مدمجة |
| **Modular** | كل وظيفة في ملف مستقل قابل للتوسيع |
| **MITRE-Mapped** | كل اقتراح مربوط بإطار ATT&CK |

---

## 2. المشكلة والحل

### المشكلة

اختبار الاختراق التقليدي يتطلب:
- حفظ **500+ أمر** عبر أدوات مختلفة
- معرفة متى تستخدم أي أداة
- تحليل النتائج يدوياً
- كتابة التقارير ساعات

### الحل — DRKagi

```
مختبر تقليدي:                    DRKagi:
nmap -sV -sC -O -T4 ...           DRKagi > scan 10.10.10.5
[يتذكر flags]                      [AI يختار الـ flags الصح]
hydra -L ... -P ... ssh://...      DRKagi > brute force SSH
[يبحث عن wordlist]                 [AI يولد wordlist مخصصة]
searchsploit apache 2.4.49         DRKagi > find exploits
[يقرأ النتائج يدوي]                [AI يشرح ويقترح التالي]
```

---

## 3. المعمارية التقنية

### مخطط المعمارية

```
┌─────────────────────────────────────────────────────────────┐
│                     DRKagi v0.3 Architecture                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐    ┌─────────────────────────────────────┐   │
│  │  User    │───▶│           drkagi.py (REPL)            │   │
│  │ (Terminal│    │   30+ commands, context tracking     │   │
│  └──────────┘    └──────────────┬──────────────────────┘   │
│                                 │                           │
│           ┌─────────────────────▼──────────────────────┐   │
│           │              agent.py (AI Brain)            │   │
│           │   Llama 3.3 70B | MITRE | Chain-of-Thought  │   │
│           │   Personas | Compliance | Attack Trees       │   │
│           └────────────┬───────────────────────────────┘   │
│                        │                                    │
│      ┌─────────────────▼──────────────────────┐            │
│      │         api_middleware.py               │            │
│      │   30 Groq Keys | Rotation | Cooldown   │            │
│      └─────────────────────────────────────────┘            │
│                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │executor.py│ │database.py│ │logger.py │ │pdf_reporter  │  │
│  │Local cmds │ │SQLite DB │ │JSONL logs│ │ReportLab PDF │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘  │
│                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │profiles.py│ │vault.py  │ │personas.py│ │api_server.py │  │
│  │Engagement │ │Encrypted │ │5 AI Modes│ │Flask REST API│  │
│  │Profiles   │ │Vault     │ │          │ │7 Endpoints   │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘  │
│                                                             │
│  ┌──────────┐ ┌──────────────┐ ┌───────────────────────┐  │
│  │plugin_   │ │session_      │ │     dashboard.py       │  │
│  │loader.py │ │manager.py    │ │  Streamlit Web UI      │  │
│  │Custom    │ │Save/Resume   │ │  Network Topology      │  │
│  │Plugins   │ │Conversations │ │                        │  │
│  └──────────┘ └──────────────┘ └───────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### تدفق البيانات

```
User Input ──▶ drkagi.py REPL
                    │
                    ├── Built-in command? ──▶ Handle directly
                    │
                    └── AI query? ──▶ agent.py
                                          │
                                          ├── Build system prompt
                                          │   (+ persona + context)
                                          │
                                          └── api_middleware.py
                                                    │
                                                    ├── Pick best key
                                                    ├── Call Groq API
                                                    └── JSON response
                                                          │
                                              ┌───────────▼──────────┐
                                              │ Display + Execute?    │
                                              │ User confirms (y/n/e) │
                                              └───────────┬──────────┘
                                                          │
                                                    executor.py
                                                          │
                                              ┌───────────▼──────────┐
                                              │ stdout + stderr       │
                                              │ ──▶ agent.analyze()   │
                                              │ ──▶ database.store()  │
                                              │ ──▶ logger.log()      │
                                              │ ──▶ Next step suggest │
                                              └──────────────────────┘
```

---

## 4. الملفات والوحدات التفصيلية

### 📄 `config.py` — نظام التكوين

**الهدف:** تحميل إعدادات المشروع مع fallback ذكي.

**ميزة فريدة:** نظام تحميل المفاتيح من 3 مصادر:
```python
# المرحلة 1: يقرأ .env (GROQ_API_KEYS) — يدمجه مع hardcoded
# المرحلة 2: يقرأ .env (GROQ_API_KEY) — يضيف hardcoded pool
# المرحلة 3: بلا .env — يستخدم 30 مفتاح hardcoded مباشرة
```

**النتيجة:** DRKagi يعمل بـ **صفر إعداد** — انسخ المجلد وشغّل.

---

### 📄 `api_middleware.py` — نظام إدارة المفاتيح

**الهدف:** إدارة 30+ مفتاح Groq API مع تدوير تلقائي.

**كيف يعمل:**
```
طلب AI جديد
    │
    ▼
get_client(strategy="least_used")
    │
    ├── يختار المفتاح الأقل استخداماً
    │
    ▼
نجح؟ ──▶ يُرجع النتيجة
    │
فشل (Rate Limit)?
    │
    ├── mark_key_failed(key) — يُعطّل المفتاح مؤقتاً
    ├── يجرب المفتاح التالي
    │
كل المفاتيح فشلت?
    │
    ├── cooldown_round 1: ينتظر 30 ثانية
    ├── cooldown_round 2: ينتظر 60 ثانية
    └── cooldown_round 3: ينتظر 90 ثانية، وإلا يرمي خطأ
```

**استراتيجيات التدوير:**
| الاستراتيجية | الوصف |
|-------------|-------|
| `least_used` | المفتاح الأقل استخداماً (افتراضي) |
| `round_robin` | دوري — الأول، الثاني، الثالث... |
| `random` | عشوائي |

---

### 📄 `agent.py` — الدماغ AI

**الهدف:** التفاعل مع Groq API وتوليد اقتراحات pentesting.

**الوظائف الرئيسية:**

| الدالة | الغرض |
|--------|-------|
| `get_suggestion(task)` | اقتراح أمر لمهمة معينة |
| `analyze_output(cmd, output)` | تحليل نتيجة أمر والاقتراح التالي |
| `generate_script(task, lang)` | كتابة Script Python/Node.js |
| `simulate_attack(scenario)` | محاكاة هجوم بدون تنفيذ |
| `generate_wordlist(target)` | توليد wordlist مخصصة |
| `check_compliance(framework, data)` | فحص امتثال PCI/HIPAA/ISO |
| `generate_attack_tree(history)` | رسم شجرة هجوم Mermaid |
| `set_context(key, value)` | ضبط سياق الهدف |
| `set_persona(addon)` | تفعيل شخصية AI |

**بنية JSON الاستجابة:**
```json
{
  "thinking": "💭 الهدف لديه منفذ SSH مفتوح، الخطوة التالية...",
  "explanation": "تعداد خدمات SSH للبحث عن إصدارات قديمة",
  "command": "nmap -sV -p 22 --script ssh-* 10.10.10.5",
  "risk_level": "Medium",
  "tool_used": "nmap",
  "mitre_id": "T1046"
}
```

---

### 📄 `drkagi.py` — نقطة الدخول والـ REPL

**الهدف:** واجهة المستخدم النصية مع 30+ أمر.

**نظام السياق:**
```python
current_target = None  # الهدف النشط

# عند كتابة: target 10.10.10.5
current_target = "10.10.10.5"
agent.set_context("target", current_target)
# كل أسئلة AI تُضخ فيها: "[Active target: 10.10.10.5] ..."
```

**أنواع الأوامر:**
- **Direct:** `clear`, `history`, `status`, `help` — تُنفَّذ مباشرة
- **Manager:** `profile`, `session`, `vault`, `plugins` — تفتح نظام فرعي
- **AI-driven:** كل شيء آخر → `agent.get_suggestion()` → تأكيد المستخدم → تنفيذ

---

### 📄 `executor.py` — تنفيذ الأوامر محلياً

**الهدف:** تنفيذ أوامر الـ terminal على Kali Linux.

```python
stdout, stderr = local_exec.execute("nmap -sV 10.10.10.5", timeout=120)
```

**الميزات:**
- Timeout قابل للضبط (افتراضي 60 ثانية، autopilot 180 ثانية)
- يُرجع stdout و stderr منفصلين
- يُضيف `PATH` لـ Kali tools

---

### 📄 `personas.py` — شخصيات AI

**الهدف:** تغيير سلوك الذكاء الاصطناعي حسب نوع المهمة.

| الشخصية | الرمز | التخصص | الاستخدام |
|---------|-------|---------|-----------|
| `stealth` | 👻 Ghost | تعقب أقصى، T0، proxychains | شبكات مراقبة |
| `aggressive` | ⚡ Blitz | كل المنافذ، T5، عدواني | CTF محدود الوقت |
| `ctf` | 🏴 CTF Hunter | أعلام، credentials افتراضية | Capture The Flag |
| `recon` | 🔍 Recon | OSINT سلبي، بدون فحص نشط | استخبارات سلبية |
| `web` | 🌐 Web Hunter | SQLi، XSS، SSRF | اختبار تطبيقات ويب |

---

### 📄 `vault.py` — خزنة Credentials

**الهدف:** تخزين credentials مكتشفة بتشفير AES-128 (Fernet).

**كيف يعمل التشفير:**
```python
# عند إنشاء الخزنة: يولد مفتاح تشفير فريد
key = Fernet.generate_key()  # مخزن في vault/.vault_key

# عند الحفظ:
f = Fernet(key)
encrypted = f.encrypt(b"admin:password123")  # → مشفّر

# عند القراءة:
decrypted = f.decrypt(encrypted).decode()   # → نص واضح
```

---

### 📄 `profiles.py` — إدارة المشاريع

**الهدف:** حفظ حالة الـ engagement كاملة (أهداف، منافذ، ثغرات) بـ JSON.

```json
{
  "name": "htb_machine_1",
  "created": "2026-02-19T14:30:00",
  "targets": [...],
  "ports": [...],
  "vulnerabilities": [...]
}
```

---

### 📄 `api_server.py` — REST API

**الهدف:** تحويل DRKagi لـ API يمكن استدعاؤه من Burp Suite، ZAP، scripts.

**المسارات:**
```
GET  /api/health          → {"status": "ok", "version": "0.3.0"}
POST /api/suggest         → {"task": "scan 10.10.10.5"} → اقتراح AI
POST /api/analyze         → {"command": "...", "output": "..."} → تحليل
POST /api/script          → {"task": "...", "lang": "python"} → Script
GET  /api/targets         → قائمة الأهداف من قاعدة البيانات
POST /api/simulate        → {"scenario": "..."} → محاكاة
GET  /api/cve?service=apache&version=2.4.49 → CVEs
```

---

### 📄 `dashboard.py` — لوحة التحكم البصرية

**الهدف:** واجهة ويب Streamlit لعرض البيانات بشكل مرئي.

**ما تعرضه:**
- إجمالي الأهداف، المنافذ، الثغرات
- جدول الأهداف المكتشفة
- جدول المنافذ المفتوحة
- خريطة شبكة تفاعلية (PyVis)
- آخر الإدخالات من قاعدة البيانات

---

### 📄 `cve_lookup.py` — البحث عن ثغرات CVE

**الهدف:** البحث في قاعدة بيانات NVD عن CVEs لخدمة وإصدار معين.

```python
vulns = cve_search.search_cve("apache", "2.4.49")
# → [{"id": "CVE-2021-41773", "severity": "CRITICAL", ...}]
```

---

### 📄 `plugin_loader.py` — نظام الإضافات

**الهدف:** تحميل plugins مخصصة تلقائياً من مجلد `plugins/`.

**بنية Plugin:**
```python
# plugins/my_tool.py
COMMAND = "mycommand"
DESCRIPTION = "ماذا يفعل هذا الأمر"

def run(args, context):
    console = context["console"]
    agent = context["agent"]
    local_exec = context["local_exec"]
    target = context["target"]
    # منطقك هنا
```

---

## 5. ميزات المنتج الكاملة

### Tier 1 — الأساسيات المحسّنة
| # | الميزة | الوصف |
|---|--------|-------|
| 1 | **CLI Flags** | `--version`, `--help`, `--api` |
| 2 | **clear** | مسح الشاشة |
| 3 | **history** | آخر 20 أمر في الجلسة |
| 4 | **export md** | تصدير الجلسة بصيغة Markdown |
| 5 | **status** | إحصائيات API، قاعدة البيانات، plugins |
| 6 | **API Cooldown** | 3 دورات انتظار بدلاً من الانهيار |

### Tier 2 — ميزات متقدمة
| # | الميزة | الملف | الوصف |
|---|--------|-------|-------|
| 7 | **Target Profiles** | `profiles.py` | حفظ/تحميل مشاريع engagement |
| 8 | **Plugin System** | `plugin_loader.py` | إضافات مخصصة قابلة للتوسيع |
| 9 | **Multi-target Autopilot** | `drkagi.py` | اختبار شبكة CIDR كاملة |
| 10 | **Session Resume** | `session_manager.py` | استكمال محادثات AI بعد الإغلاق |
| 11 | **Wordlist Manager** | `agent.py` | توليد wordlists مخصصة بالذكاء الاصطناعي |
| 12 | **Attack Tree** | `agent.py` | مخططات Mermaid لمسارات الهجوم |

### Tier 3 — مستوى عالمي
| # | الميزة | الوصف |
|---|--------|-------|
| 13 | **MITRE ATT&CK** | كل اقتراح يحمل معرّف T#### |
| 14 | **AI Personas** | 5 شخصيات متخصصة |
| 15 | **Chain-of-Thought** | AI يُظهر تفكيره قبل الأمر |
| 16 | **Credential Vault** | خزنة مشفرة AES للـ credentials |
| 17 | **Dockerfile** | صورة Docker على Kali Linux |
| 18 | **install.sh** | مثبّت بسطر واحد على Kali |
| 19 | **Compliance Check** | PCI-DSS, HIPAA, ISO 27001 |
| 20 | **REST API** | 7 Flask endpoints للتكامل |

---

## 6. كيفية الاستخدام — شرح تفصيلي

### التثبيت والإعداد

```bash
# الطريقة 1: مباشرة
git clone https://github.com/yourusername/DRKagi.git
cd DRKagi
pip install -r requirements.txt
python drkagi.py

# الطريقة 2: Docker
docker build -t drkagi .
docker run -it drkagi

# الطريقة 3: Kali one-liner
curl -sL https://raw.githubusercontent.com/yourusername/DRKagi/main/install.sh | bash
```

**ملاحظة:** لا حاجة لإعداد `.env` — المفاتيح مدمجة تلقائياً.

---

### سيناريو 1: اختبار هدف واحد

```bash
# 1. شغّل DRKagi
python drkagi.py

# 2. حدد الهدف (AI يقترح أول خطوة تلقائياً)
DRKagi > target 10.10.10.5

# 3. AI يقترح:
# 💭 "Target set. Starting with stealth port scan..."
# Command: nmap -sC -sV -T4 10.10.10.5

# 4. اقبل بـ y
Execute? (y/n/e=edit): y

# 5. DRKagi يُنفّذ، يُحلّل، يقترح التالي تلقائياً
# Recommended next step: hydra -l admin -P /usr/share/wordlists/rockyou.txt ssh://10.10.10.5
```

---

### سيناريو 2: Autopilot على شبكة كاملة

```bash
DRKagi > autopilot 192.168.1.0/24

# المرحلة 0: اكتشاف الأجهزة الحية
# → nmap -sn -T4 192.168.1.0/24
# Found 5 live hosts: 192.168.1.1, .5, .10, .20, .100

# لكل جهاز تلقائياً:
# HOST 1/5: 192.168.1.1
# [RECON] → [ENUM] → [VULNSCAN] → [EXPLOIT]
```

---

### سيناريو 3: تخصيص شخصية AI

```bash
# للاختبار الخفي (محاكمة جدار ناري ذكي)
DRKagi > persona stealth
# 👻 Ghost activated! Maximum evasion mode.

# الآن كل اقتراحات AI ستكون:
# -T0-T1 (بطيء جداً لتجنب IDS)
# decoy scans (-D)
# fragmentation (-f)
# proxychains tunneling

# للـ CTF
DRKagi > persona ctf
# 🏴 CTF Hunter activated! Flag hunting mode.
# → يبحث عن default credentials
# → يفحص GTFOBins
# → يبحث عن SUID bits
```

---

### سيناريو 4: كتابة Script مخصص

```bash
DRKagi > write script scan all ports and save results to file

# AI يكتب:
# ── drkagi_script.py ──────────────────
# import subprocess
# import sys
# target = sys.argv[1]
# result = subprocess.run(['nmap', '-p-', '-T4', target], ...)
# with open(f'scan_{target}.txt', 'w') as f:
#     f.write(result.stdout)
```

---

### سيناريو 5: إدارة نتائج الـ engagement

```bash
# حفظ مشروع
DRKagi > profile save htb_machine_1

# رؤية الأهداف المكتشفة
DRKagi > show targets

# حفظ المحادثة لاستكمالها لاحقاً
DRKagi > session save htb_session_1
# أغلق DRKagi

# في اليوم التالي
DRKagi > session load htb_session_1
# → استكمل من حيث توقفت، AI يتذكر كل شيء
```

---

### سيناريو 6: التحقق من الامتثال

```bash
DRKagi > compliance pci
# ──────────────────────────────────────────────
# PCI-DSS Compliance Report
# Score: 4/10
# FAIL  Req 6.1: Unpatched systems found (Apache 2.4.49 CVE-2021-41773)
# FAIL  Req 8.2: SSH allows password auth (should use keys only)
# PASS  Req 1.1: Firewall rules applied on perimeter
# FAIL  Req 10.5: Audit logs not encrypted
```

---

## 7. مسار التعلم — من المبتدئ للمتقدم

### 🟢 المستوى الأول: المبتدئ (أسبوع 1-2)

**مفاهيم يجب تعلمها:**
- ما هو اختبار الاختراق؟
- ما هو الـ Red Team؟
- مراحل اختبار الاختراق (Reconnaissance → Exploitation → Post-Exploitation)

**أوامر DRKagi للبداية:**
```bash
help                    # اقرأ كل الأوامر
target <IP>             # حدد هدفاً
scan <IP>               # اقرأ النتائج وافهمها
status                  # افهم كيف يعمل النظام
```

**تمارين عملية:**
1. شغّل DRKagi وافحص جهازك الخاص: `target 127.0.0.1`
2. اقرأ نتائج nmap وافهم كل سطر
3. جرب `help` وافهم كل أمر

**موارد التعلم:**
- [TryHackMe](https://tryhackme.com/) — مسار "Pre-Security"
- [Kali Linux Revealed](https://kali.training/) — مجاني
- كتاب "Penetration Testing" - Georgia Weidman

---

### 🟡 المستوى الثاني: المتوسط (أسبوع 3-6)

**مفاهيم يجب تعلمها:**
- Network scanning وتفسير نتائج nmap
- Service enumeration (HTTP, SSH, FTP, SMB)
- CVE databases والبحث عن ثغرات
- Password attacks وWordlists

**أوامر DRKagi:**
```bash
persona recon           # تعلم الـ reconnaissance
wordlist <target>       # فهم كيف تُبنى wordlists
persona web             # تعلم Web Application Testing
compliance pci          # افهم أطر الامتثال
```

**تمارين عملية:**
1. اشترك في [HackTheBox](https://hackthebox.com/) — ابدأ بـ "Starting Point"
2. استخدم DRKagi على الأجهزة التدريبية
3. افهم كل MITRE ATT&CK ID تراه في اقتراحات DRKagi

**أدوات تعلمها:**
| الأداة | الاستخدام |
|--------|----------|
| `nmap` | Port scanning |
| `gobuster` | Directory brute force |
| `sqlmap` | SQL injection automated |
| `hydra` | Password brute force |
| `nikto` | Web vulnerability scanner |

---

### 🔴 المستوى الثالث: المتقدم (شهر 2-4)

**مفاهيم يجب تعلمها:**
- Exploitation وPost-Exploitation
- Privilege Escalation (Linux/Windows)
- Active Directory attacks
- Evasion techniques

**أوامر DRKagi:**
```bash
persona aggressive      # تعلم الهجوم المباشر
autopilot 10.10.10.0/24 # اختبر شبكة كاملة
attack map              # افهم مسارات الهجوم
simulate lateral movement in AD  # تعلم AD attacks
```

**تمارين عملية:**
1. أكمل 10 أجهزة على HackTheBox
2. جرب [ProLabs](https://app.hackthebox.com/prolabs) - RastaLabs أو Offshore
3. ابنِ Lab خاص بك باستخدام VirtualBox

**شهادات يمكن استهدافها:**
| الشهادة | المستوى | التركيز |
|---------|---------|---------|
| **CompTIA Security+** | مبتدئ | أساسيات الأمن |
| **CEH** | متوسط | Ethical Hacking |
| **OSCP** | متقدم | Practical Exploitation |
| **CRTE** | متقدم | Active Directory |

---

### 🟣 المستوى الرابع: الخبير (مستمر)

**تطوير DRKagi نفسه:**

**فهم الكود (لمبرمجين مبتدئين):**
```python
# ابدأ بـ config.py — الأبسط
# فهم كيف تُقرأ متغيرات البيئة

# ثم executor.py — فهم subprocess
import subprocess
result = subprocess.run(["nmap", "-sV", "10.10.10.5"],
                       capture_output=True, text=True)
print(result.stdout)  # النتيجة

# ثم api_middleware.py — فهم API calls
# ثم agent.py — فهم كيف تُبنى prompts
```

**إنشاء Plugin خاص:**
```python
# plugins/my_sqli.py
COMMAND = "sqli"
DESCRIPTION = "AI-guided SQL injection test"

def run(args, context):
    target = args or context.get("target", "")
    agent = context["agent"]
    console = context["console"]
    
    console.print(f"[bold]Testing SQLi on: {target}[/bold]")
    suggestion = agent.get_suggestion(
        f"Find SQL injection vulnerabilities on {target}"
    )
    console.print(suggestion)
```

---

## 8. التطوير والتوسيع

### هيكل المشروع للمطور

```
DRKagi/
├── config.py           # إعداد — ابدأ هنا
├── api_middleware.py   # إدارة API keys
├── agent.py            # AI brain — أهم ملف
├── drkagi.py             # REPL — منطق التحكم
├── executor.py         # تنفيذ أوامر
├── database.py         # SQLite ORM
├── logger.py           # تسجيل الجلسات
├── cve_lookup.py       # NVD API
├── pdf_reporter.py     # PDF generation
├── dashboard.py        # Streamlit UI
├── profiles.py         # Engagement profiles
├── plugin_loader.py    # Plugin system
├── session_manager.py  # AI session persistence
├── personas.py         # AI personality modes
├── vault.py            # Encrypted credential storage
├── api_server.py       # Flask REST API
├── plugins/            # ← ضع plugins هنا
│   └── example_plugin.py
├── Dockerfile          # Docker image
├── install.sh          # Installer
└── requirements.txt    # Python dependencies
```

### إضافة أداة جديدة لـ AI

في `agent.py`، في قسم ATTACK TOOLS، أضف:
```python
"  - mytool: يفعل كذا وكذا. Usage: mytool -opt target\n"
```

### إضافة أمر جديد للـ REPL

في `drkagi.py`، قبل قسم AI SUGGESTION FLOW:
```python
if cmd.startswith('mycommand'):
    parts = user_input.split()
    # منطقك هنا
    continue
```

### تعديل System Prompt

في `agent.py`، الدالة `_initialize_system_prompt()`:
```python
# أضف تعليماتك هنا — AI سيتبعها
"  - افعل كذا عند...\n"
"  - لا تفعل كذا أبداً...\n"
```

---

## 9. الأمان والأخلاقيات

> **⚠️ تحذير قانوني صريح**
>
> DRKagi أداة مصممة **حصراً** لاختبار الأمان **المرخّص**. استخدامها على أنظمة بدون إذن صريح كتابي **جريمة جنائية** في معظم دول العالم.

### الاستخدام المسموح
- ✅ شبكاتك وأجهزتك الخاصة
- ✅ بيئات التدريب (TryHackMe, HackTheBox)
- ✅ العملاء الذين وقّعت معهم عقد pentest مكتوب
- ✅ Labs محلية مُعدّة للتدريب

### الاستخدام الممنوع
- ❌ أي جهاز لا تملكه أو لا تملك إذناً كتابياً
- ❌ الشبكات العامة
- ❌ الحكومات، البنوك، المستشفيات بدون عقد

### الـ API Keys
- المفاتيح الحالية للتطوير والتدريب فقط
- للاستخدام في الإنتاج: احصل على مفاتيحك من [console.groq.com](https://console.groq.com)
- لا تشارك مفاتيح API في كود عام

---

## 10. خطط المستقبل

### الإصدار 0.4 (المرحلة القادمة)
- [ ] **Memory Persistence** — AI يتذكر نتائج الجلسات السابقة تلقائياً
- [ ] **Auto-Exploitation** — يجرب exploits تلقائياً في sandbox
- [ ] **Report Templates** — قوالب تقارير جاهزة (Executive, Technical, Compliance)
- [ ] **Interactive Network Map** — خريطة شبكة تتحدث بالوقت الفعلي

### الإصدار 0.5 (قريباً)
- [ ] **Voice Commands** — أوامر صوتية بالعربية والإنجليزية
- [ ] **Team Mode** — عدة مختبرين على نفس الجلسة
- [ ] **Automated Reporting** — تقارير PDF كاملة بضغطة واحدة
- [ ] **C2 Framework** — Metasploit integration مخصص

### الرؤية الطويلة المدى
- اعتماد DRKagi بواسطة فرق Red Team المحترفة
- شهادة Certified DRKagi Operator (CDO)
- مجتمع مفتوح المصدر لتطوير plugins

---

## الخلاصة

**DRKagi v0.3** ليس مجرد أداة — إنه **مساعد ذكي** يفهم ما تريد فعله أمنياً، يختار الأداة الصحيحة، يُنفّذ، يُحلّل، ويقترح الخطوة التالية. كل هذا مع الحفاظ على:

- 🔒 **الأمان:** Credential Vault مشفّر، `.env` محمي من Git
- 📋 **التوثيق:** كل جلسة مسجلة، قابلة للتصدير والتقرير
- 🧠 **الذكاء:** MITRE ATT&CK mapping، chain-of-thought، personas
- 🔧 **التوسعية:** Plugin system، REST API، Docker

```
Think like an attacker. Act like a professional.
DRKagi v0.3.0 — Ready for deployment.
```

---

<div align="center">
<i>وثيقة تقنية شاملة — DRKagi v0.3.0 — فبراير 2026</i>
</div>
