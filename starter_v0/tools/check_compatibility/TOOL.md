---
name: check_compatibility
track: core
kind: local_knowledge
requires_env: []
inputs: [cpu_sku, mainboard_sku, ram_sku, gpu_sku, psu_sku, case_sku, cooler_sku, use_case]
outputs: [compatible, issues, warnings, details]
side_effect: false
---
# check_compatibility

Kiểm tra độ tương thích phần cứng giữa CPU, Bo mạch chủ (Mainboard), RAM, Card đồ họa (GPU), Nguồn (PSU) và Tản nhiệt (Cooler).
Xác thực tương thích socket (LGA1700, AM5), chuẩn RAM (DDR4/DDR5) và tổng công suất nguồn điện yêu cầu.
