import psutil
import platform
import cpuinfo
import subprocess
import mmap
from fpdf import FPDF
from datetime import datetime

class UltimateReport(FPDF):
    def header(self):
        self.set_fill_color(44, 62, 80)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 20)
        self.cell(0, 15, 'HARDWARE INTEGRITY & LIFECYCLE REPORT', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 5, 'Comprehensive System Internals & Purchase Diagnostics', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Data-Systems-Internals Project | Generated: {datetime.now()} | Page {self.page_no()}', 0, 0, 'C')

    def section_header(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 236, 241)
        self.set_text_color(31, 73, 125)
        self.cell(0, 10, f"  {title}", 0, 1, 'L', 1)
        self.ln(3)
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', '', 10)

def get_size(bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes < 1024: return f"{bytes:.2f}{unit}"
        bytes /= 1024

def get_ssd_status():
    try:
        raw_status = subprocess.check_output("wmic diskdrive get status", shell=True).decode()
        return raw_status.strip().split("\n")[-1].strip()
    except: return "Unable to fetch (Admin rights needed)"

def generate_3_page_report():
    # --- Data Collection ---
    c = cpuinfo.get_cpu_info()
    mem = psutil.virtual_memory()
    disk_io = psutil.disk_io_counters()
    battery = psutil.sensors_battery()
    cpu_stats = psutil.cpu_stats()
    net_io = psutil.net_io_counters()
    partitions = psutil.disk_partitions()

    pdf = UltimateReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- PAGE 1: SYSTEM & CPU ---
    pdf.add_page()
    
    pdf.section_header("1. BASIC SYSTEM IDENTIFICATION")
    pdf.cell(0, 7, f"Machine Name: {platform.node()}", 0, 1)
    pdf.cell(0, 7, f"Operating System: {platform.system()} {platform.release()} (Ver: {platform.version()})", 0, 1)
    pdf.cell(0, 7, f"Architecture: {platform.machine()} / {platform.processor()}", 0, 1)
    pdf.ln(5)

    pdf.section_header("2. PROCESSOR (CPU) DEEP-DIVE")
    pdf.cell(0, 7, f"Full Model: {c.get('brand_raw', 'Unknown')}", 0, 1)
    pdf.cell(0, 7, f"Core Count: {psutil.cpu_count(logical=False)} Physical / {psutil.cpu_count(logical=True)} Logical", 0, 1)
    pdf.cell(0, 7, f"Current Frequency: {psutil.cpu_freq().current:.2f} MHz", 0, 1)
    pdf.cell(0, 7, f"L2 Cache: {c.get('l2_cache_size', 'N/A')} | L3 Cache: {c.get('l3_cache_size', 'N/A')}", 0, 1)
    pdf.ln(5)

    pdf.section_header("3. KERNEL & MULTITASKING PERFORMANCE")
    pdf.cell(0, 7, f"Context Switches: {cpu_stats.ctx_switches:,} (High value indicates multitasking load)", 0, 1)
    pdf.cell(0, 7, f"System Interrupts: {cpu_stats.interrupts:,}", 0, 1)
    pdf.cell(0, 7, f"Uptime: {round((time.time() - psutil.boot_time())/3600, 2)} Hours", 0, 1)

    # --- PAGE 2: MEMORY & STORAGE ---
    pdf.add_page()
    
    pdf.section_header("4. MEMORY & VIRTUAL STORAGE")
    pdf.cell(0, 7, f"Total Physical RAM: {get_size(mem.total)}", 0, 1)
    pdf.cell(0, 7, f"Used RAM: {get_size(mem.used)} ({mem.percent}%)", 0, 1)
    pdf.cell(0, 7, f"Available RAM: {get_size(mem.available)}", 0, 1)
    pdf.cell(0, 7, f"Swap (Virtual) Memory: {psutil.swap_memory().percent}% Used", 0, 1)
    pdf.ln(5)

    pdf.section_header("5. STORAGE HARDWARE & SSD HEALTH")
    pdf.cell(0, 7, f"S.M.A.R.T. Hardware Status: {get_ssd_status()}", 0, 1)
    pdf.cell(0, 7, f"Total Lifetime Reads: {get_size(disk_io.read_bytes)}", 0, 1)
    pdf.cell(0, 7, f"Total Lifetime Writes: {get_size(disk_io.write_bytes)}", 0, 1)
    pdf.ln(3)
    pdf.cell(0, 7, "Partition Details:", 0, 1, 'L')
    for p in partitions:
        try:
            usage = psutil.disk_usage(p.mountpoint)
            pdf.cell(0, 7, f"  - {p.device} ({p.mountpoint}): {usage.percent}% Full of {get_size(usage.total)}", 0, 1)
        except: continue
    pdf.ln(5)

    # --- PAGE 3: BATTERY & EXPERT VERDICT ---
    pdf.add_page()
    
    pdf.section_header("6. BATTERY HEALTH (FOR LAPTOPS)")
    if battery:
        pdf.cell(0, 7, f"Battery Level: {battery.percent}%", 0, 1)
        pdf.cell(0, 7, f"Power Source: {'Plugged In' if battery.power_plugged else 'On Battery'}", 0, 1)
        # Wear level context
        if battery.percent < 100 and battery.power_plugged:
            pdf.cell(0, 7, "Note: Battery not reaching 100%? Potential cell degradation.", 0, 1)
    else:
        pdf.cell(0, 7, "No Battery detected (Desktop or Faulty Connection)", 0, 1)
    pdf.ln(5)

    pdf.section_header("7. NETWORK INTERFACE DATA")
    pdf.cell(0, 7, f"Total Data Sent: {get_size(net_io.bytes_sent)}", 0, 1)
    pdf.cell(0, 7, f"Total Data Received: {get_size(net_io.bytes_recv)}", 0, 1)
    pdf.ln(5)

    # FINAL EXPERT ANALYSIS
    pdf.set_fill_color(255, 255, 204)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 12, " FINAL PURCHASE ANALYSIS & VERDICT ", 1, 1, 'C', 1)
    pdf.set_font('Arial', '', 11)
    pdf.ln(4)

    verdict_text = ""
    # Analysis Logic
    if get_ssd_status() != "OK" and get_ssd_status() != "Unknown":
        verdict_text += "- REJECT: Storage hardware is reporting FAILURE (SMART Error).\n"
    if disk_io.write_bytes > (2 * 1024**4): # Over 2TB
        verdict_text += "- WARNING: High SSD usage (Over 2TB written). SSD lifespan is reduced.\n"
    if mem.total < (8 * 1024**3): # Less than 8GB
        verdict_text += "- NOTE: RAM is less than 8GB. Might struggle with modern Urdu Novel Bank development.\n"
    
    if not verdict_text:
        verdict_text = "PASS: This machine is in excellent health. No major hardware red flags detected."
    
    pdf.multi_cell(0, 8, verdict_text)
    
    # Save PDF
    file_name = f"Hardware_Report_{datetime.now().strftime('%d%m%y')}.pdf"
    pdf.output(file_name)
    print(f"✅ 3-Page Detailed Report Generated: {file_name}")

if __name__ == "__main__":
    import time
    print("🚀 Running Deep Hardware Scan (Page 1-3)...")
    generate_3_page_report()


# import psutil
# import platform
# import mmap
# import cpuinfo
# from fpdf import FPDF
# from datetime import datetime
# import time

# class SystemReport(FPDF):
#     def header(self):
#         self.set_font('Arial', 'B', 15)
#         self.set_text_color(44, 62, 80)
#         self.cell(0, 10, 'Professional Hardware Diagnostic Report', 0, 1, 'C')
#         self.set_draw_color(44, 62, 80)
#         self.line(10, 22, 200, 22)
#         self.ln(10)

#     def footer(self):
#         self.set_y(-15)
#         self.set_font('Arial', 'I', 8)
#         self.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Page {self.page_no()}', 0, 0, 'C')

# def get_size(bytes, suffix="B"):
#     factor = 1024
#     for unit in ["", "K", "M", "G", "T", "P"]:
#         if bytes < factor:
#             return f"{bytes:.2f}{unit}{suffix}"
#         bytes /= factor

# def generate_full_hardware_report():
#     # 1. Gathering Comprehensive Data
#     cpu_info = cpuinfo.get_cpu_info()
#     mem = psutil.virtual_memory()
#     swap = psutil.swap_memory()
#     disk_io = psutil.disk_io_counters()
#     partitions = psutil.disk_partitions()
#     cpu_stats = psutil.cpu_stats()
#     battery = psutil.sensors_battery()
#     boot_time = datetime.fromtimestamp(psutil.boot_time())
#     net_io = psutil.net_io_counters()

#     # 2. PDF Setup
#     pdf = SystemReport()
#     pdf.add_page()
#     pdf.set_font("Arial", size=10)

#     # --- Section 1: Core System & CPU ---
#     pdf.set_fill_color(230, 230, 230)
#     pdf.cell(0, 10, "1. System & Processor Architecture", 0, 1, 'L', 1)
#     pdf.ln(2)
#     pdf.cell(0, 7, f"Processor: {cpu_info.get('brand_raw', 'Unknown')}", 0, 1)
#     pdf.cell(0, 7, f"Architecture: {cpu_info.get('arch', 'Unknown')} ({cpu_info.get('bits', '')} bit)", 0, 1)
#     pdf.cell(0, 7, f"Physical Cores: {psutil.cpu_count(logical=False)} | Logical Cores: {psutil.cpu_count(logical=True)}", 0, 1)
#     pdf.cell(0, 7, f"System Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
#     pdf.ln(4)

#     # --- Section 2: Memory & Thermal Health (Safely Handled) ---
#     pdf.set_fill_color(200, 220, 255)
#     pdf.cell(0, 10, "2. Memory & Thermal Status", 0, 1, 'L', 1)
#     pdf.ln(2)
#     pdf.cell(0, 7, f"Total RAM: {get_size(mem.total)} | Available: {get_size(mem.available)}", 0, 1)
#     pdf.cell(0, 7, f"Swap Total: {get_size(swap.total)} | Used: {swap.percent}%", 0, 1)
    
#     # AttributeError Check for Temperature
#     try:
#         if hasattr(psutil, "sensors_temperatures"):
#             temps = psutil.sensors_temperatures()
#             if temps:
#                 for name, entries in temps.items():
#                     pdf.cell(0, 7, f"Sensor {name}: {entries[0].current}°C", 0, 1)
#             else:
#                 pdf.cell(0, 7, "Temperature Sensors: No data returned from sensors", 0, 1)
#         else:
#             pdf.cell(0, 7, "Temperature Sensors: Not supported on this OS version", 0, 1)
#     except Exception as e:
#         pdf.cell(0, 7, f"Temperature Sensors: Could not access ({str(e)})", 0, 1)
#     pdf.ln(4)

#     # --- Section 3: Battery Health ---
#     pdf.set_fill_color(210, 255, 210)
#     pdf.cell(0, 10, "3. Battery & Power Diagnostics", 0, 1, 'L', 1)
#     pdf.ln(2)
#     if battery:
#         status = "Plugged In" if battery.power_plugged else "Discharging"
#         pdf.cell(0, 7, f"Current Charge: {battery.percent}%", 0, 1)
#         pdf.cell(0, 7, f"Power Status: {status}", 0, 1)
#         seconds = battery.secsleft
#         if seconds == psutil.POWER_TIME_UNLIMITED:
#             pdf.cell(0, 7, "Battery Life Left: Power plugged", 0, 1)
#         elif seconds == psutil.POWER_TIME_UNKNOWN:
#             pdf.cell(0, 7, "Battery Life Left: Calculating...", 0, 1)
#         else:
#             pdf.cell(0, 7, f"Estimated Life Left: {seconds // 3600}h { (seconds % 3600) // 60}m", 0, 1)
#     else:
#         pdf.cell(0, 7, "Battery Info: No battery detected", 0, 1)
#     pdf.ln(4)

#     # --- Section 4: Storage Integrity & I/O ---
#     pdf.set_fill_color(255, 230, 200)
#     pdf.cell(0, 10, "4. Storage Performance & I/O", 0, 1, 'L', 1)
#     pdf.ln(2)
#     pdf.cell(0, 7, f"Total Disk Read: {get_size(disk_io.read_bytes)} | Writes: {get_size(disk_io.write_bytes)}", 0, 1)
#     for partition in partitions:
#         try:
#             usage = psutil.disk_usage(partition.mountpoint)
#             pdf.cell(0, 7, f"Drive {partition.device}: {usage.percent}% Full of {get_size(usage.total)}", 0, 1)
#         except (PermissionError, OSError): continue
#     pdf.ln(4)

#     # --- Section 5: Network & Kernel Stress ---
#     pdf.set_fill_color(240, 200, 255)
#     pdf.cell(0, 10, "5. Network & Kernel Stress Stats", 0, 1, 'L', 1)
#     pdf.ln(2)
#     pdf.cell(0, 7, f"Context Switches: {cpu_stats.ctx_switches:,}", 0, 1)
#     pdf.cell(0, 7, f"Data Sent: {get_size(net_io.bytes_sent)} | Received: {get_size(net_io.bytes_recv)}", 0, 1)
#     pdf.ln(10)

#     # Advice Logic
#     pdf.set_font("Arial", 'B', 11)
#     pdf.cell(0, 7, "Expert Purchase Advice:", 0, 1)
#     pdf.set_font("Arial", size=10)
    
#     advice = ""
#     if disk_io.read_bytes > (1024**4): # 1 TB
#         advice += "- ALERT: This disk has processed over 1 TB of data. Check SSD health.\n"
#     if battery and battery.percent < 100 and battery.power_plugged:
#         advice += "- TIP: If battery isn't reaching 100% while plugged, it may have wear.\n"
#     if not advice:
#         advice = "- All hardware indicators are within normal operating ranges."
    
#     pdf.multi_cell(0, 7, advice)

#     # Final Output
#     save_path = r"E:\git-workstation\Data-Systems-Internals\reports\Advanced_Laptop_Diagnostic_Report.pdf"
#     pdf.output(save_path)
#     print(f"✅ Report Generated Successfully: {save_path}")

# if __name__ == "__main__":
#     print("🚀 Running Diagnostics...")
#     generate_full_hardware_report()








# import psutil
# import platform
# import mmap
# import cpuinfo
# import subprocess
# from fpdf import FPDF
# from datetime import datetime

# class SystemReport(FPDF):
#     def header(self):
#         self.set_font('Arial', 'B', 15)
#         self.set_text_color(44, 62, 80)
#         self.cell(0, 10, 'Ultimate Hardware Integrity Report', 0, 1, 'C')
#         self.line(10, 22, 200, 22)
#         self.ln(10)

#     def footer(self):
#         self.set_y(-15)
#         self.set_font('Arial', 'I', 8)
#         self.cell(0, 10, f'Confidential Diagnostic | Page {self.page_no()}', 0, 0, 'C')

# def get_size(bytes):
#     for unit in ["B", "KB", "MB", "GB", "TB"]:
#         if bytes < 1024: return f"{bytes:.2f}{unit}"
#         bytes /= 1024

# def get_ssd_health():
#     """Windows specific command to check drive health"""
#     try:
#         output = subprocess.check_output("wmic diskdrive get status", shell=True).decode()
#         return output.strip().split("\n")[-1].strip()
#     except:
#         return "Unknown"

# def generate_ultimate_report():
#     cpu_info = cpuinfo.get_cpu_info()
#     mem = psutil.virtual_memory()
#     disk_io = psutil.disk_io_counters()
#     battery = psutil.sensors_battery()
#     ssd_status = get_ssd_health()
    
#     pdf = SystemReport()
#     pdf.add_page()
#     pdf.set_font("Arial", size=10)

#     # --- Section 1: Crucial SSD Health ---
#     pdf.set_fill_color(255, 200, 200)
#     pdf.cell(0, 10, "1. STORAGE INTEGRITY (SSD/HDD)", 0, 1, 'L', 1)
#     pdf.ln(2)
#     pdf.cell(0, 7, f"Drive Hardware Status: {ssd_status} (OK means no physical sector failure)", 0, 1)
#     pdf.cell(0, 7, f"Life-time Read: {get_size(disk_io.read_bytes)}", 0, 1)
#     pdf.cell(0, 7, f"Life-time Write: {get_size(disk_io.write_bytes)}", 0, 1)
#     pdf.set_font("Arial", 'I', 9)
#     pdf.multi_cell(0, 6, "Note: If status is 'Pred Fail', do NOT buy this laptop. High Write counts on SSD reduce its lifespan.")
#     pdf.set_font("Arial", size=10)
#     pdf.ln(4)

#     # --- Section 2: Battery Wear & Cycle Context ---
#     pdf.set_fill_color(210, 255, 210)
#     pdf.cell(0, 10, "2. BATTERY WEAR & POWER", 0, 1, 'L', 1)
#     pdf.ln(2)
#     if battery:
#         pdf.cell(0, 7, f"Charge Level: {battery.percent}%", 0, 1)
#         pdf.cell(0, 7, f"Power Source: {'AC Adapter' if battery.power_plugged else 'Battery Battery'}", 0, 1)
#     else:
#         pdf.cell(0, 7, "Battery: Not detected (Check if it's a desktop or faulty battery)", 0, 1)
#     pdf.ln(4)

#     # --- Section 3: Processor Stress & RAM ---
#     pdf.set_fill_color(200, 220, 255)
#     pdf.cell(0, 10, "3. COMPUTING POWER", 0, 1, 'L', 1)
#     pdf.ln(2)
#     pdf.cell(0, 7, f"CPU: {cpu_info.get('brand_raw', 'Unknown')}", 0, 1)
#     pdf.cell(0, 7, f"Physical RAM: {get_size(mem.total)}", 0, 1)
#     pdf.cell(0, 7, f"Available RAM: {get_size(mem.available)}", 0, 1)
#     pdf.ln(4)

#     # --- Section 4: Final Verdict ---
#     pdf.set_fill_color(240, 240, 240)
#     pdf.cell(0, 10, "4. FINAL PURCHASE VERDICT", 0, 1, 'L', 1)
#     pdf.ln(2)
    
#     verdict = "PASS: Hardware seems solid for professional use."
#     if ssd_status != "OK" and ssd_status != "Unknown":
#         verdict = "REJECT: Storage hardware reporting errors!"
#     elif disk_io.write_bytes > (2048 * 1024**3): # 2TB+ Writes
#         verdict = "WARNING: Heavy SSD usage detected (Over 2TB written). Negotiate price."
    
#     pdf.set_font("Arial", 'B', 12)
#     pdf.cell(0, 10, verdict, 0, 1)

#     save_path = "Laptop_Final_Check_Report.pdf"
#     pdf.output(save_path)
#     print(f"✅ Ultimate Report Saved: {save_path}")

# if __name__ == "__main__":
#     generate_ultimate_report()











# import psutil
# import platform
# import mmap
# import cpuinfo
# from fpdf import FPDF
# from datetime import datetime

# class SystemReport(FPDF):
#     def header(self):
#         self.set_font('Arial', 'B', 15)
#         self.cell(0, 10, 'Data-Systems-Internals: Advanced Hardware Profile', 0, 1, 'C')
#         self.ln(5)

#     def footer(self):
#         self.set_y(-15)
#         self.set_font('Arial', 'I', 8)
#         self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# def generate_advanced_pdf_report():
#     # 1. Gathering Existing & New Data
#     cpu_data = cpuinfo.get_cpu_info()
#     mem = psutil.virtual_memory()
#     swap = psutil.swap_memory()
#     disk = psutil.disk_io_counters()
#     cpu_stats = psutil.cpu_stats()
    
#     # 2. PDF Setup
#     pdf = SystemReport()
#     pdf.add_page()
#     pdf.set_font("Arial", size=11)

#     # --- Section 1: Memory & Virtual Storage ---
#     pdf.set_fill_color(200, 220, 255)
#     pdf.cell(0, 10, "1. Memory & Virtual Storage (Swap)", 0, 1, 'L', 1)
#     pdf.ln(2)
#     pdf.cell(0, 7, f"Total Physical RAM: {round(mem.total / (1024**3), 2)} GB", 0, 1)
#     pdf.cell(0, 7, f"OS Page Size: {mmap.PAGESIZE} bytes", 0, 1)
#     pdf.cell(0, 7, f"Total Swap Space: {round(swap.total / (1024**3), 2)} GB", 0, 1)
#     pdf.cell(0, 7, f"Swap Usage: {swap.percent}%", 0, 1)
#     pdf.ln(5)

#     # --- Section 2: Disk I/O Performance ---
#     pdf.cell(0, 10, "2. Storage I/O Throughput", 0, 1, 'L', 1)
#     pdf.ln(2)
#     pdf.cell(0, 7, f"Read Count: {disk.read_count:,}", 0, 1)
#     pdf.cell(0, 7, f"Write Count: {disk.write_count:,}", 0, 1)
#     pdf.cell(0, 7, f"Total Read: {round(disk.read_bytes / (1024**3), 2)} GB", 0, 1)
#     pdf.cell(0, 7, f"Total Write: {round(disk.write_bytes / (1024**3), 2)} GB", 0, 1)
#     pdf.ln(5)

#     # --- Section 3: OS Kernel & CPU Stats ---
#     pdf.cell(0, 10, "3. Kernel & Multitasking Stats", 0, 1, 'L', 1)
#     pdf.ln(2)
#     pdf.cell(0, 7, f"Context Switches: {cpu_stats.ctx_switches:,}", 0, 1)
#     pdf.cell(0, 7, f"Interrupts: {cpu_stats.interrupts:,}", 0, 1)
#     pdf.cell(0, 7, f"Soft Interrupts: {cpu_stats.soft_interrupts:,}", 0, 1)
#     pdf.ln(5)

#     # --- Section 4: Data Engineering Impact ---
#     pdf.cell(0, 10, "4. Advanced Engineering Context", 0, 1, 'L', 1)
#     pdf.ln(2)
#     insight_text = (
#         f"Context Switching: Your system has performed {cpu_stats.ctx_switches:,} switches. "
#         "High context switching can lead to TLB flushes and increased EAT. "
#         f"Disk I/O: Total read of {round(disk.read_bytes / (1024**3), 2)} GB suggests the "
#         "intensity of data movement between storage and RAM."
#     )
#     pdf.multi_cell(0, 7, insight_text)
    
#     # Save PDF
#     file_name = r"E:\git-workstation\Data-Systems-Internals\reports\Advanced_System_Report.pdf"
#     pdf.output(file_name)
#     print(f"✅ Advanced PDF Report Generated: {file_name}")

# if __name__ == "__main__":
#     generate_advanced_pdf_report()












# import psutil
# import platform
# import mmap
# import cpuinfo
# from fpdf import FPDF
# from datetime import datetime

# class SystemReport(FPDF):
#     def header(self):
#         self.set_font('Arial', 'B', 15)
#         self.cell(0, 10, 'Data-Systems-Internals: Hardware Profile', 0, 1, 'C')
#         self.ln(5)

#     def footer(self):
#         self.set_y(-15)
#         self.set_font('Arial', 'I', 8)
#         self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# def generate_pdf_report():
#     # 1. Gathering Data
#     cpu_data = cpuinfo.get_cpu_info()
#     mem = psutil.virtual_memory()
    
#     # 2. PDF Setup
#     pdf = SystemReport()
#     pdf.add_page()
#     pdf.set_font("Arial", size=11)

#     # --- Section: Basic Info ---
#     pdf.set_fill_color(200, 220, 255)
#     pdf.cell(0, 10, "1. General System Information", 0, 1, 'L', 1)
#     pdf.ln(2)
#     pdf.cell(0, 7, f"OS: {platform.system()} {platform.release()}", 0, 1)
#     pdf.cell(0, 7, f"Processor: {cpu_data['brand_raw']}", 0, 1)
#     pdf.cell(0, 7, f"Architecture: {platform.machine()}", 0, 1)
#     pdf.ln(5)

#     # --- Section: Memory & Paging ---
#     pdf.cell(0, 10, "2. Memory & Paging Internals", 0, 1, 'L', 1)
#     pdf.ln(2)
#     pdf.cell(0, 7, f"Total RAM: {round(mem.total / (1024**3), 2)} GB", 0, 1)
#     pdf.cell(0, 7, f"OS Page Size: {mmap.PAGESIZE} bytes", 0, 1)
#     pdf.cell(0, 7, f"L2 Cache: {cpu_data.get('l2_cache_size', 'N/A')}", 0, 1)
#     pdf.cell(0, 7, f"L3 Cache: {cpu_data.get('l3_cache_size', 'N/A')}", 0, 1)
#     pdf.ln(5)

#     # --- Section: Data Engineering Insights ---
#     pdf.cell(0, 10, "3. Data Engineering Context", 0, 1, 'L', 1)
#     pdf.ln(2)
#     pdf.multi_cell(0, 7, (
#         "Effective Access Time (EAT) Note: Based on your hardware, memory access is "
#         "optimized for sequential (Row-Major) data processing. Large L3 cache suggests "
#         "high performance for vectorized operations in NumPy/Pandas."
#     ))
   
#     # Save PDF
#     file_name = r"E:\git-workstation\Data-Systems-Internals\reports\System_Hardware_Report.pdf"
#     pdf.output(file_name)
#     print(f"✅ PDF Report Generated: {file_name}")

# if __name__ == "__main__":
#     generate_pdf_report()