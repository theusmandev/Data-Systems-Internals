import psutil
import platform
import mmap
import cpuinfo
from fpdf import FPDF
from datetime import datetime
import time

class SystemReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.set_text_color(44, 62, 80)
        self.cell(0, 10, 'Professional Hardware Diagnostic Report', 0, 1, 'C')
        self.set_draw_color(44, 62, 80)
        self.line(10, 22, 200, 22)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Page {self.page_no()}', 0, 0, 'C')

def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def generate_full_hardware_report():
    # 1. Gathering Comprehensive Data
    cpu_info = cpuinfo.get_cpu_info()
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk_io = psutil.disk_io_counters()
    partitions = psutil.disk_partitions()
    cpu_stats = psutil.cpu_stats()
    battery = psutil.sensors_battery()
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    net_io = psutil.net_io_counters()

    # 2. PDF Setup
    pdf = SystemReport()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # --- Section 1: Core System & CPU ---
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, "1. System & Processor Architecture", 0, 1, 'L', 1)
    pdf.ln(2)
    pdf.cell(0, 7, f"Processor: {cpu_info.get('brand_raw', 'Unknown')}", 0, 1)
    pdf.cell(0, 7, f"Architecture: {cpu_info.get('arch', 'Unknown')} ({cpu_info.get('bits', '')} bit)", 0, 1)
    pdf.cell(0, 7, f"Physical Cores: {psutil.cpu_count(logical=False)} | Logical Cores: {psutil.cpu_count(logical=True)}", 0, 1)
    pdf.cell(0, 7, f"System Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
    pdf.ln(4)

    # --- Section 2: Memory & Thermal Health ---
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(0, 10, "2. Memory & Thermal Status", 0, 1, 'L', 1)
    pdf.ln(2)
    pdf.cell(0, 7, f"Total RAM: {get_size(mem.total)} | Available: {get_size(mem.available)}", 0, 1)
    pdf.cell(0, 7, f"Swap Total: {get_size(swap.total)} | Used: {swap.percent}%", 0, 1)
    
    # Temperature (Note: May not work on all Windows machines without admin/specific drivers)
    temps = psutil.sensors_temperatures()
    if temps:
        for name, entries in temps.items():
            pdf.cell(0, 7, f"Sensor {name}: {entries[0].current}°C", 0, 1)
    else:
        pdf.cell(0, 7, "Temperature Sensors: Not accessible (Check BIOS/Admin rights)", 0, 1)
    pdf.ln(4)

    # --- Section 3: Battery Health (Crucial for Laptops) ---
    pdf.set_fill_color(210, 255, 210)
    pdf.cell(0, 10, "3. Battery & Power Diagnostics", 0, 1, 'L', 1)
    pdf.ln(2)
    if battery:
        status = "Plugged In" if battery.power_plugged else "Discharging"
        pdf.cell(0, 7, f"Current Charge: {battery.percent}%", 0, 1)
        pdf.cell(0, 7, f"Power Status: {status}", 0, 1)
        seconds = battery.secsleft
        if seconds == psutil.POWER_TIME_UNLIMITED:
            pdf.cell(0, 7, "Battery Life Left: Unlimited (Power plugged)", 0, 1)
        elif seconds == psutil.POWER_TIME_UNKNOWN:
            pdf.cell(0, 7, "Battery Life Left: Calculating...", 0, 1)
        else:
            pdf.cell(0, 7, f"Estimated Life Left: {seconds // 3600}h { (seconds % 3600) // 60}m", 0, 1)
    else:
        pdf.cell(0, 7, "Battery Info: No battery detected (Is this a Desktop?)", 0, 1)
    pdf.ln(4)

    # --- Section 4: Storage Integrity & I/O ---
    pdf.set_fill_color(255, 230, 200)
    pdf.cell(0, 10, "4. Storage Performance & I/O", 0, 1, 'L', 1)
    pdf.ln(2)
    pdf.cell(0, 7, f"Total Disk Read: {get_size(disk_io.read_bytes)} | Writes: {get_size(disk_io.write_bytes)}", 0, 1)
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            pdf.cell(0, 7, f"Drive {partition.device} ({partition.fstype}): {usage.percent}% Full of {get_size(usage.total)}", 0, 1)
        except PermissionError: continue
    pdf.ln(4)

    # --- Section 5: Network & Kernel Stress ---
    pdf.set_fill_color(240, 200, 255)
    pdf.cell(0, 10, "5. Network & Kernel Stress Stats", 0, 1, 'L', 1)
    pdf.ln(2)
    pdf.cell(0, 7, f"Context Switches: {cpu_stats.ctx_switches:,} (Multitasking Load)", 0, 1)
    pdf.cell(0, 7, f"Data Sent: {get_size(net_io.bytes_sent)} | Received: {get_size(net_io.bytes_recv)}", 0, 1)
    pdf.ln(10)

    # --- Expert Insight Summary ---
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 7, "Expert Purchase Advice:", 0, 1)
    pdf.set_font("Arial", size=10)
    
    advice = ""
    if battery and battery.percent < 50 and not battery.power_plugged:
        advice += "- WARNING: Battery level low. Check for rapid discharge.\n"
    if swap.percent > 10:
        advice += "- NOTE: High swap usage detected. Consider upgrading RAM for better performance.\n"
    if disk_io.read_bytes > (500 * 1024**3):
        advice += "- ALERT: High Disk Read (Over 500GB). This machine has been heavily used.\n"
    
    if not advice:
        advice = "- System looks stable based on current hardware counters."
        
    pdf.multi_cell(0, 7, advice)

    # Final Output
    save_path = r"E:\git-workstation\Data-Systems-Internals\reports\Laptop_Diagnostic_Report.pdf"
    pdf.output(save_path)
    print(f"✅ Full Diagnostic Report Generated: {save_path}")

if __name__ == "__main__":
    print("🚀 Starting Deep System Scan...")
    generate_full_hardware_report()






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