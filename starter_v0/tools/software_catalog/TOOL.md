---
name: software_catalog
track: bonus
kind: local_inventory
provider: mock_software_catalog
requires_env: []
inputs: [software_name, category]
outputs: [software_name, approval_status, version, license_required, license_type, install_method, notes]
side_effect: false
requires_confirmation: false
---

# Tool: software_catalog (Bonus Technical Tool)

## 1. Purpose
Tra cứu danh mục phần mềm nội bộ của Northstar Labs để kiểm tra:
- Tình trạng cấp phép (`approval_status`: `approved`, `restricted`, `prohibited`).
- Yêu cầu bản quyền (`license_required`, `license_type`).
- Phương thức cài đặt hợp lệ (`install_method`).
- Các lưu ý tuân thủ chính sách IT (`notes`).

Giúp nhân viên và kỹ thuật viên Helpdesk biết ngay phần mềm nào được phép tự cài đặt qua Company Portal, phần mềm nào cần duyệt bản quyền qua ticket, phần mềm nào bị hạn chế (như Wireshark), và phần mềm nào bị cấm triệt để (như BitTorrent).

## 2. Input Schema
- `software_name` (string, required): Tên phần mềm cần tra cứu (ví dụ: `Docker Desktop`, `VS Code`, `Wireshark`, `BitTorrent`). Hỗ trợ tìm kiếm không phân biệt chữ hoa/thường và theo alias.
- `category` (string, optional, default: `"all"`): Phân loại phần mềm (`all`, `development`, `communication`, `security`, `collaboration`, `utilities`).

## 3. Output Schema
- Thành công:
  ```json
  {
    "tool": "software_catalog",
    "software_name": "Docker Desktop",
    "found": true,
    "approval_status": "approved",
    "version": "4.33.1",
    "category": "development",
    "license_required": true,
    "license_type": "Docker Business Subscription",
    "install_method": "Request license via IT Ticket, then install via Company Portal",
    "notes": "Requires manager approval for license cost allocation ($24/user/mo)."
  }
  ```
- Không tìm thấy (`software_not_found`):
  ```json
  {
    "tool": "software_catalog",
    "software_name": "unknown_app",
    "found": false,
    "error": "software_not_found",
    "message": "Phần mềm 'unknown_app' không có trong danh mục nội bộ của Northstar Labs. Vui lòng liên hệ IT Helpdesk hoặc tạo yêu cầu đánh giá an ninh phần mềm."
  }
  ```

## 4. Safety & Privacy Guardrails
- **Read-only**: Không thay đổi trạng thái hệ thống, `side_effect: false`, không yêu cầu bước xác nhận.
- **Data boundaries**: Toàn bộ dữ liệu là mock data nội bộ, không gọi API ra bên ngoài, không lưu trữ token/credentials.
- **Policy enforcement**: Phản hồi rõ ràng nếu phần mềm thuộc diện `prohibited` (vi phạm chính sách bảo mật SEC-09) hoặc `restricted` (chỉ dành cho NetOps/SecOps).
