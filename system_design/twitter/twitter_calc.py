# filename: twitter_calc.py

# Assumptions
num_daus = 1000000000
requests_per_dau = 5
storage_per_request = 10 * 1024  # 10 KB in bytes
bandwidth_per_request = 100 * 1024  # 100 KB in bytes

# Calculations
total_requests_per_day = num_daus * requests_per_dau
rps = total_requests_per_day / (24 * 60 * 60)
total_storage_per_day = total_requests_per_day * storage_per_request
total_bandwidth_per_day = total_requests_per_day * bandwidth_per_request

# Write to markdown file
with open('twitter_calc.md', 'w') as file:
    file.write("# Twitter Calculation Results\n\n")
    file.write(f"Requests Per Second (RPS): {rps:.2f}\n\n")
    file.write(f"Storage per Day: {total_storage_per_day / (1024**3):.2f} GB\n\n")
    file.write(f"Bandwidth per Day: {total_bandwidth_per_day / (1024**3):.2f} GB\n\n")

print("Calculation results have been written to twitter_calc.md.")