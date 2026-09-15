---
name: check_compatibility
track: core
kind: local_knowledge
provider: pc_seller_data/catalog.json
requires_env: []
inputs: [cpu_sku, mainboard_sku, ram_sku, gpu_sku, psu_sku, case_sku, cooler_sku, use_case]
outputs: [compatible, checks, failed_checks, requested]
side_effect: false
---
# check_compatibility

Checks a build against catalog specs: CPU socket vs mainboard socket, mainboard
memory type vs memory kit, GPU length vs case clearance, PSU wattage vs GPU
recommendation, and CPU socket vs cooler support. Unknown SKUs return
`error: sku_not_found`.
