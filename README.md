# ClinIQ – Smart Clinic Queue & Appointment System  
**No more waiting in line! Book, check-in, and track with AI**

![ClinIQ Logo](https://via.placeholder.com/800x400.png?text=ClinIQ+Smart+Clinic)  
*AI-Powered • Easy to Use • Works in India, Japan & Worldwide*

---

## What is ClinIQ?

**ClinIQ** is a **simple, smart clinic system** that helps:

- **Patients**:  
  - Check-in with **QR code**  
  - **Book appointments** online  
  - **See free time slots**  
  - **Track your position** in queue  
  - **Get AI tips** on best time to visit  

- **Doctors**:  
  - See who’s next  
  - Call patient with **one click**  
  - View today’s appointments  

- **Admins**:  
  - See **live queue** for all departments  
  - View **AI reports**: busiest day, best hour  
  - **Download patient data** (CSV)

---

## Features

| Feature | What It Does |
|--------|-------------|
| **QR Check-in** | Scan or show QR at counter |
| **Book Appointment** | Pick from **free slots only** |
| **Real-time Queue** | See your position & wait time |
| **AI Triage** | Urgent cases (chest pain) go first |
| **Smart Tips** | “Best time to visit: Tuesday 10 AM” |
| **Phone Validation** | Works for **India**, **Japan**, **Others** |
| **No Internet Needed** | Runs on local computer |

---

## Works in These Countries

| Country | Phone Format |
|--------|-------------|
| India | `9876543210` (10 digits, starts 6–9) |
| Japan | `09012345678` (10–11 digits, starts 0) |
| Others | Any 7–15 digit number |

---

## How to Use (Step-by-Step)

### 1. **Start the App**

1. Open the **ClinIQ** folder on your computer.  
2. Double-click `RUN_CLiniQ.bat` → A browser opens automatically.  

> **Done!** No coding needed.

---

### 2. **Choose Your Role**

On the left side, click:

| Role | Who Uses |
|------|---------|
| **Patient** | You (to check-in or book) |
| **Doctor** | Doctor or nurse |
| **Admin** | Clinic manager |

---

### 3. **For Patients**

#### Check-in (Walk-in)
1. Click **"Check-in"** tab  
2. Fill:  
   - Full Name  
   - Country (India / Japan / Other)  
   - Phone (see hint)  
   - Department  
   - Symptoms (optional)  
3. Click **"Check-in Now"**  
4. **Show QR code** at reception  

> You’re in the queue!

#### Track Your Queue
1. Enter your **Token** (from QR)  
2. Click **"Check Status"**  
3. See:  
   - Your position  
   - Estimated wait time  

#### Book Appointment
1. Click **"Book Appointment"**  
2. Fill name, phone, country  
3. Pick **date**  
4. See **available time slots** (30-min gaps)  
5. Pick one → Click **"Book"**  
6. Get confirmation + AI tip  

---

### 4. **For Doctors**

1. Select your **Department**  
2. See **queue list**  
3. Click **"CALL NEXT"** → Patient is notified  
4. See today’s booked appointments  

---

### 5. **For Admins**

1. **Live Queues**: See how many waiting in each dept  
2. **AI Analytics**:  
   - Most free hour  
   - Busiest day  
   - Heatmap of patient load  
3. **Export**: Click to download all data in Excel (CSV)

---

## Departments Available

- General  
- Cardiology  
- Pediatrics  
- Orthopedics  

---

## Phone Number Rules (Important!)

| Country | Example | Rule |
|--------|--------|------|
| India | `9876543210` | 10 digits, start with 6,7,8,9 |
| Japan | `09012345678` | 10 or 11 digits, start with 0 |
| Other | `+12025550123` | 7 to 15 digits |

> App shows **live hint** when you select country.

---

## Files in This Folder (Don’t Delete!)

| File | What It Is |
|-----|-----------|
| `app.py` | Main program (don’t edit) |
| `RUN_CLiniQ.bat` | Double-click to start |
| `cliniq.db` | Your clinic data (auto-created) |
| `requirements.txt` | Needed software |
| `pages/` | Internal code |
| `README.md` | This file |

---

## How to Start (One-Click)

### Windows (Most Clinics)
1. **Double-click** `RUN_CLiniQ.bat`  
2. Wait 10 seconds → Browser opens  
3. Use the app!

> **No internet needed**  
> **Works offline**

