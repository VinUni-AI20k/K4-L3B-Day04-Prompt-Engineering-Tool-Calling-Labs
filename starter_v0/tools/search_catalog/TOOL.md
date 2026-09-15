---
name: search_catalog
track: core
kind: local_knowledge
requires_env: []
inputs: [category, use_case, budget_max, query]
outputs: [total_found, items]
side_effect: false
---
# search_catalog

Tra cứu danh mục linh kiện máy tính và dàn PC lắp sẵn theo phân loại (category: cpu, prebuilt, ram, storage, monitor, cooler, gpu, mainboard, psu), nhu cầu sử dụng (use_case: gaming, office, workstation), mức ngân sách tối đa (budget_max), hoặc từ khóa tự do (query).
