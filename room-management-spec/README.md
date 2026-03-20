# Hệ Thống Quản Lý Phòng Trọ - Specification

Đồ án sinh viên Kỹ thuật lập trình. Ứng dụng desktop quản lý phòng trọ với Python + PyQt6, kiến trúc MVC, lưu trữ đa định dạng (JSON/XML/XLSX). Hỗ trợ 2 roles: Admin (toàn quyền) và Guest (khách thuê).

## Quy tắc bắt buộc

### Terminology

LUÔN dùng `guest` thay vì `tenant` ở MỌI NƠI:

| Sai | Đúng |
|-----|------|
| `tenant`, `Tenant`, `tenant_id` | `guest`, `Guest`, `guest_id` |
| `TenantRepository`, `TenantService` | `GuestRepository`, `GuestService` |
| `tenants.xlsx` | `guests.xlsx` |
| "Quản lý khách thuê" | "Quản lý khách" |

### Data Storage Strategy

| Format | Files | Lý do |
|--------|-------|-------|
| JSON | `users.json`, `rooms.json`, `system_settings.json` | Truy xuất nhanh, cấu trúc đơn giản |
| XML | `contracts.xml`, `rental_applications.xml`, `repair_requests.xml` | Dữ liệu phân cấp |
| XLSX | `guests.xlsx`, `invoices.xlsx` | Dữ liệu dạng bảng, reporting |

### Contract Flow

Hỗ trợ **2 cách** tạo hợp đồng:
1. Guest chọn phòng → Điền thông tin cá nhân → Hợp đồng tạo tự động (không cần Admin duyệt)
2. Admin tạo trực tiếp (cho khách walk-in)

### Invoice Flow

Tại mục **quản lý phòng** của admin: Bấm nút **"Tạo hóa đơn hàng tháng"** → hệ thống tự động kết nối IoT ghi nhận điện nước → tính tiền → tạo hóa đơn cho tất cả phòng đang thuê.

### UI Strategy

UI đã được làm sẵn bằng PyQt6. **KHÔNG tự tạo UI mới.** Khi implement:
- Phase 1-6: Chỉ làm backend (models, handlers, repositories, services)
- Phase 7: User gửi code UI → merge vào folder `ui/` → kết nối với backend services

## Thứ tự đọc & thực thi

1. **`requirements.md`** — 20 requirements, 100 acceptance criteria. Hiểu hệ thống CẦN LÀM GÌ.
2. **`design.md`** — Architecture, data models, interfaces, constants. Hiểu hệ thống ĐƯỢC THIẾT KẾ NHƯ THẾ NÀO.
3. **`tasks.md`** — Implementation roadmap 7 phases (Phase 1-6 backend, Phase 7 merge UI). Follow để IMPLEMENT TỪNG BƯỚC.
