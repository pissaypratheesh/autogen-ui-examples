# filename: Ola_calc.py

# Assumptions
num_daus = 1000000000
requests_per_dau = 10
storage_per_request = 1  # KB
bandwidth_per_request = 10  # KB

# Calculations
total_requests_per_day = num_daus * requests_per_dau
rps = total_requests_per_day / (24 * 60 * 60)
total_storage_per_day = total_requests_per_day * storage_per_request
total_storage_per_month = total_storage_per_day * 30
total_bandwidth_per_day = total_requests_per_day * bandwidth_per_request
total_bandwidth_per_month = total_bandwidth_per_day * 30

# Writing to Markdown file
with open("Ola_calc.md", "w") as file:
    file.write("# Ola Calculation Results\n\n")
    file.write("## Requests Per Second (RPS)\n\n")
    file.write(f"RPS: {rps:.2f}\n\n")
    file.write("## Storage Requirements\n\n")
    file.write(f"Total storage per day: {total_storage_per_day} KB\n\n")
    file.write(f"Total storage per month: {total_storage_per_month} KB\n\n")
    file.write("## Bandwidth Requirements\n\n")
    file.write(f"Total bandwidth per day: {total_bandwidth_per_day} KB\n\n")
    file.write(f"Total bandwidth per month: {total_bandwidth_per_month} KB\n\n")

print("Calculation results have been written to Ola_calc.md.")