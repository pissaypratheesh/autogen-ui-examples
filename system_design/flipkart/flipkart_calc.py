# filename: flipkart_calc.py

# Assumptions
number_of_daus = 1000000000
average_requests_per_user_per_day = 10
average_size_of_request = 1 * 1024  # 1 KB in bytes
average_images_loaded_per_user_per_day = 5
average_size_of_image = 100 * 1024  # 100 KB in bytes
average_videos_loaded_per_user_per_day = 1
average_size_of_video = 10 * 1024 * 1024  # 10 MB in bytes
average_other_files_loaded_per_user_per_day = 2
average_size_of_other_file = 500 * 1024  # 500 KB in bytes

# Calculations
total_number_of_requests_per_day = number_of_daus * average_requests_per_user_per_day
rps = total_number_of_requests_per_day / (24 * 60 * 60)

total_storage_required_per_day = (number_of_daus * average_images_loaded_per_user_per_day * average_size_of_image) + \
                                 (number_of_daus * average_videos_loaded_per_user_per_day * average_size_of_video) + \
                                 (number_of_daus * average_other_files_loaded_per_user_per_day * average_size_of_other_file)

total_bandwidth_required_per_day = total_storage_required_per_day + total_number_of_requests_per_day

# Create the markdown content
markdown_content = f"""
# Flipkart Calculation

## Requests Per Second (RPS)
- RPS: {rps}

## Storage Requirements
- Storage required per day: {total_storage_required_per_day / (1024 * 1024 * 1024)} GB

## Bandwidth Requirements
- Bandwidth required per day: {total_bandwidth_required_per_day / (1024 * 1024 * 1024)} GB
"""

# Write the markdown content to the file
with open("flipkart_calc.md", "w") as file:
    file.write(markdown_content)

print("Markdown file 'flipkart_calc.md' created successfully.")