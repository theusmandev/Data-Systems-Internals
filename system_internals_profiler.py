


import psutil
import platform
import mmap
import cpuinfo
from fpdf import FPDF
from datetime import datetime

class SystemReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Data-Systems-Internals: Advanced Hardware Profile', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_advanced_pdf_report():
    # 1. Gathering Existing & New Data
    cpu_data = cpuinfo.get_cpu_info()
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_io_counters()
    cpu_stats = psutil.cpu_stats()
    
    # 2. PDF Setup
    pdf = SystemReport()
    pdf.add_page()
    pdf.set_font("Arial", size=11)

    # --- Section 1: Memory & Virtual Storage ---
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(0, 10, "1. Memory & Virtual Storage (Swap)", 0, 1, 'L', 1)
    pdf.ln(2)
    pdf.cell(0, 7, f"Total Physical RAM: {round(mem.total / (1024**3), 2)} GB", 0, 1)
    pdf.cell(0, 7, f"OS Page Size: {mmap.PAGESIZE} bytes", 0, 1)
    pdf.cell(0, 7, f"Total Swap Space: {round(swap.total / (1024**3), 2)} GB", 0, 1)
    pdf.cell(0, 7, f"Swap Usage: {swap.percent}%", 0, 1)
    pdf.ln(5)

    # --- Section 2: Disk I/O Performance ---
    pdf.cell(0, 10, "2. Storage I/O Throughput", 0, 1, 'L', 1)
    pdf.ln(2)
    pdf.cell(0, 7, f"Read Count: {disk.read_count:,}", 0, 1)
    pdf.cell(0, 7, f"Write Count: {disk.write_count:,}", 0, 1)
    pdf.cell(0, 7, f"Total Read: {round(disk.read_bytes / (1024**3), 2)} GB", 0, 1)
    pdf.cell(0, 7, f"Total Write: {round(disk.write_bytes / (1024**3), 2)} GB", 0, 1)
    pdf.ln(5)

    # --- Section 3: OS Kernel & CPU Stats ---
    pdf.cell(0, 10, "3. Kernel & Multitasking Stats", 0, 1, 'L', 1)
    pdf.ln(2)
    pdf.cell(0, 7, f"Context Switches: {cpu_stats.ctx_switches:,}", 0, 1)
    pdf.cell(0, 7, f"Interrupts: {cpu_stats.interrupts:,}", 0, 1)
    pdf.cell(0, 7, f"Soft Interrupts: {cpu_stats.soft_interrupts:,}", 0, 1)
    pdf.ln(5)

    # --- Section 4: Data Engineering Impact ---
    pdf.cell(0, 10, "4. Advanced Engineering Context", 0, 1, 'L', 1)
    pdf.ln(2)
    insight_text = (
        f"Context Switching: Your system has performed {cpu_stats.ctx_switches:,} switches. "
        "High context switching can lead to TLB flushes and increased EAT. "
        f"Disk I/O: Total read of {round(disk.read_bytes / (1024**3), 2)} GB suggests the "
        "intensity of data movement between storage and RAM."
    )
    pdf.multi_cell(0, 7, insight_text)
    
    # Save PDF
    file_name = r"E:\git-workstation\Data-Systems-Internals\reports\Advanced_System_Report.pdf"
    pdf.output(file_name)
    print(f"✅ Advanced PDF Report Generated: {file_name}")

if __name__ == "__main__":
    generate_advanced_pdf_report()












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