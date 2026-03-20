# Implementation Tasks - Hệ Thống Quản Lý Phòng Trọ

## Overview

Roadmap triển khai hệ thống theo 7 phases. Phase 1-6 là **backend thuần** (business logic, data). Phase 7 là **merge UI có sẵn** (user đã làm PyQt6 UI riêng, chỉ cần link với backend). Mỗi phase kết thúc bằng checkpoint.

## Phase 1: Core Infrastructure

> **Mục tiêu**: Project structure, file handlers, cấu hình cơ bản.
> **Dependencies**: Không có.

**Task 1.1: Project setup**
- Tạo directory structure theo design.md (Project Structure section)
- Tạo virtual environment, cài dependencies từ requirements.txt
- Tạo `config/constants.py` với tất cả file paths và status constants
- Tạo `config/settings.py` với system configuration management
- _Req: 17.4, 17.5_

**Task 1.2: JSON Handler**
- Implement `JSONHandler` class với load/save/add/update/delete/find_by_id/get_all
- Auto-create file nếu chưa tồn tại, auto-generate ID (last_id pattern)
- Error handling cho malformed JSON
- _Req: 15.1, 15.6_

**Task 1.3: XML Handler**
- Implement `XMLHandler` class với load/save/add/update/delete/element_to_dict/get_all
- Support root_tag và item_tag parameters
- Error handling cho malformed XML
- _Req: 15.2, 15.6_

**Task 1.4: Excel Handler**
- Implement `ExcelHandler` class với load/save/add_row/update_row/delete_row/find_by_id/get_all
- Auto-create file nếu chưa tồn tại, auto-generate ID
- _Req: 15.3, 15.6_

**Checkpoint 1**: Tất cả handlers hoạt động đúng, đọc/ghi round-trip chính xác.

---

## Phase 2: Data Models

> **Mục tiêu**: 7 data models với validation và serialization.
> **Dependencies**: Phase 1 (handlers).

**Task 2.1: User model**
- Implement `User` dataclass với set_password/check_password (bcrypt), to_dict/from_dict
- Validate email format và phone format
- _Req: 1.1, 2.3, 19.1_

**Task 2.2: Room model**
- Implement `Room` dataclass với is_available(), to_dict/from_dict
- Status chỉ chấp nhận values từ ROOM_STATUS constants
- _Req: 3.1, 3.5_

**Task 2.3: Guest model**
- Implement `Guest` dataclass với to_dict/from_dict
- Link tới User qua user_id FK
- _Req: 4.1, 6.3_

**Task 2.4: Contract model**
- Implement `Contract` dataclass với is_active/is_expired/days_until_expiry, to_dict/from_dict
- Contract number format: HD[YYYY][MM][NNN]
- _Req: 8.2, 8.3, 8.4_

**Task 2.5: Invoice model**
- Implement `Invoice` dataclass với is_overdue/days_overdue, to_dict/from_dict
- Invoice number format: INV[YYYY][MM][NNN]
- total_amount = room_rent + electricity_cost + water_cost + other_fees
- _Req: 10.2, 10.3_

**Task 2.6: Application model**
- Implement `Application` dataclass với to_dict/from_dict
- _Req: 6.1, 6.4_

**Task 2.7: RepairRequest model**
- Implement `RepairRequest` dataclass với to_dict/from_dict
- _Req: 14.1, 14.2_

**Task 2.8: Validators utility**
- Implement `utils/validators.py`: validate_email(), validate_phone(), validate_status(), sanitize_input()
- _Req: 2.2, 19.5_

**Checkpoint 2**: Tất cả models serialize/deserialize đúng, validation hoạt động.

---

## Phase 3: Repository Layer

> **Mục tiêu**: CRUD repositories cho tất cả entities.
> **Dependencies**: Phase 1 (handlers) + Phase 2 (models).

**Task 3.1: BaseRepository**
- Implement generic base class với get_by_id/get_all/create/update/delete
- _Req: 15.5_

**Task 3.2: UserRepository (JSON)**
- Extend BaseRepository, thêm get_by_email/get_by_phone/authenticate
- Storage: users.json, list_key='users'
- _Req: 1.1, 2.5_

**Task 3.3: RoomRepository (JSON)**
- Extend BaseRepository, thêm get_available_rooms/get_by_status
- Storage: rooms.json, list_key='rooms'
- _Req: 3.1, 3.2, 5.4_

**Task 3.4: GuestRepository (XLSX)**
- Extend BaseRepository, thêm get_by_user_id/search
- Storage: guests.xlsx
- _Req: 4.3, 15.3_

**Task 3.5: ContractRepository (XML)**
- Extend BaseRepository, thêm get_active_contracts/get_by_guest_id/get_by_room_id/get_expired_contracts
- Storage: contracts.xml, root='contracts', item='contract'
- _Req: 8.1, 8.4, 15.2_

**Task 3.6: InvoiceRepository (XLSX)**
- Extend BaseRepository, thêm get_by_contract_id/get_by_status/get_overdue
- Storage: invoices.xlsx
- _Req: 10.5, 12.1, 12.3_

**Task 3.7: ApplicationRepository (XML)**
- Extend BaseRepository, thêm get_by_guest_id/get_by_room_id
- Storage: rental_applications.xml, root='applications', item='application'
- _Req: 6.5, 7.1_

**Task 3.8: RepairRequestRepository (XML)**
- Extend BaseRepository, thêm get_by_guest_id/get_by_room_id/get_by_status
- Storage: repair_requests.xml, root='repair_requests', item='repair_request'
- _Req: 14.5_

**Checkpoint 3**: Tất cả repositories CRUD hoạt động đúng.

---

## Phase 4: Authentication Service

> **Mục tiêu**: Login, register, session management.
> **Dependencies**: Phase 3 (UserRepository).

**Task 4.1: AuthService**
- Implement login (email/phone + password → bcrypt verify)
- Implement register (validate → check duplicate → hash password → create user with role='guest')
- Implement logout, get_current_user, is_admin
- Session tracking (current_user state)
- _Req: 1.1-1.5, 2.1-2.5_

**Task 4.2: Session timeout**
- Implement auto-logout after configurable inactivity period
- _Req: 19.4_

**Checkpoint 4**: Auth hoạt động đầy đủ (login, register, logout, session).

---

## Phase 5: Business Logic Services

> **Mục tiêu**: Core business services cho room, guest, contract, invoice, application, repair.
> **Dependencies**: Phase 3 (repositories) + Phase 4 (auth).

**Task 5.1: RoomService**
- CRUD với validation (prevent delete occupied room)
- Status management, availability filtering
- `filter_rooms_by_status(status)`: lọc phòng theo trống (available) / đang thuê (occupied)
- _Req: 3.1-3.7, 5.1-5.5_

**Task 5.2: GuestService**
- CRUD với validation
- `search_guests_by_name(name)`: tìm kiếm khách theo tên
- `filter_guests_by_rental_status(status)`: lọc theo đang thuê (active) / sắp hết hạn (expiring, <=30 ngày) / đã chấm dứt (terminated)
- Cần inject ContractRepository để tra cứu trạng thái hợp đồng của guest
- _Req: 4.1-4.7_

**Task 5.3: ApplicationService (Rental Registration)**
- register_rental: Guest chọn phòng → điền thông tin cá nhân → tự động tạo contract + cập nhật room status (không cần admin duyệt)
- Validate room available trước khi đăng ký, prevent booking occupied rooms
- cancel_registration: Hủy đăng ký (cập nhật status, terminate contract, free room)
- get_all_registrations / get_registrations_by_guest cho admin xem lịch sử
- _Req: 6.1-6.6, 7.1-7.5_

**Task 5.4: ContractService**
- Create contract (manual or from approved application)
- Generate unique contract number HD[YYYY][MM][NNN]
- Terminate contract (update room status to available)
- Check expired contracts
- Generate HTML from template, export PDF
- _Req: 8.1-8.6, 9.1-9.5_

**Task 5.5: IoTService**
- Simulate meter readings (electricity + water) that increase over time
- Calculate utility consumption (current - previous readings)
- Configurable rates, manual override fallback
- _Req: 11.1-11.5_

**Task 5.6: InvoiceService**
- `generate_monthly_invoices(month, year)`: Khi admin bấm "Tạo hóa đơn hàng tháng" tại mục quản lý phòng:
  1. Kết nối IoT → ghi nhận chỉ số điện/nước cho tất cả phòng đang thuê
  2. Tính consumption = current - previous, nhân đơn giá
  3. Tạo hóa đơn cho từng hợp đồng active
  4. Cập nhật previous_reading = current_reading
- Generate unique invoice number INV[YYYY][MM][NNN]
- Due date = created_at + 5 days
- Mark as paid, detect overdue
- `filter_invoices(month, year, paid)`: lọc theo tháng/năm + trạng thái
- _Req: 10.1-10.7, 12.1-12.6_

**Task 5.7: RepairRequestService**
- Submit request (guest), update status (admin)
- Filter by guest/room/status
- _Req: 14.1-14.6_

**Checkpoint 5**: Toàn bộ business logic hoạt động.

---

## Phase 6: System Services

> **Mục tiêu**: Backup, config, reporting, security, performance.
> **Dependencies**: Phase 5 (all business services).

**Task 6.1: BackupService**
- Auto daily backup (copy all data files to backups/ with timestamp)
- Manual backup trigger
- Restore from backup (validate integrity before applying)
- Cleanup backups older than retention period
- _Req: 16.1-16.5_

**Task 6.2: ReportService**
- Monthly revenue reports (total income, unpaid, overdue)
- Room occupancy statistics
- Guest retention/turnover rates
- Export to PDF and Excel
- _Req: 18.1-18.5_

**Task 6.3: Audit logging**
- Log all user actions with timestamp, user_id, action, details
- _Req: 19.3_

**Task 6.4: Input validation & sanitization**
- Comprehensive validation cho tất cả user inputs
- Protection against injection attacks
- _Req: 19.5_

**Task 6.5: Pagination**
- Implement pagination cho data queries exceeding page size
- _Req: 20.5_

**Task 6.6: ServiceContainer**
- Implement `config/container.py` singleton DI container
- Wire tất cả repositories và services
- Export container interface để UI gọi được

**Checkpoint 6**: System services hoạt động, backend hoàn chỉnh.

---

## Phase 7: UI Integration (Merge UI có sẵn)

> **Mục tiêu**: Merge code UI PyQt6 đã có sẵn vào project, kết nối với backend services.
> **Dependencies**: Phase 6 (all backend services) + UI code từ user.
> **LƯU Ý**: KHÔNG tự tạo UI mới. User đã làm sẵn UI bằng PyQt6, chỉ cần nhận code và link.

**Task 7.1: Nhận và merge UI code**
- User gửi code UI PyQt6 → copy vào folder `ui/`
- Xác định mapping: UI component nào gọi service nào

**Task 7.2: Kết nối UI → Backend**
- Connect UI login/register forms → AuthService
- Connect UI admin screens → RoomService, GuestService, ContractService, InvoiceService, ReportService
- **Mục quản lý phòng (admin)**: Nút "Tạo hóa đơn hàng tháng" → InvoiceService.generate_monthly_invoices(month, year) → hệ thống kết nối IoT ghi nhận điện nước rồi tạo hóa đơn
- Connect UI guest screens → RoomService (browse), ApplicationService (đăng ký thuê), InvoiceService (xem hóa đơn), RepairRequestService
- Truyền ServiceContainer vào MainWindow và các UI components

**Task 7.3: Event handlers & data binding**
- Wire button clicks, form submissions → service method calls
- Load data từ services vào tables/lists
- Handle service responses (success/error) → hiển thị message cho user
- Role-based UI visibility (admin vs guest)

**Task 7.4: UI-specific validation & UX**
- Loading indicators cho operations > 2 seconds
- Error message dialogs cho validation/business rule errors
- Pagination controls cho large datasets
- _Req: 20.3, 20.4, 20.5_

**Checkpoint 7**: UI đã merge, hoạt động với tất cả backend services. Hệ thống hoàn chỉnh.

---

## Summary

| Phase | Tasks | Mục tiêu |
|-------|-------|----------|
| 1. Infrastructure | 1.1-1.4 | File handlers (JSON, XML, XLSX) + config |
| 2. Data Models | 2.1-2.8 | 7 models + validators |
| 3. Repositories | 3.1-3.8 | CRUD repositories cho tất cả entities |
| 4. Authentication | 4.1-4.2 | Login, register, session |
| 5. Business Logic | 5.1-5.7 | Room, Guest, Application, Contract, IoT, Invoice, Repair |
| 6. System Services | 6.1-6.6 | Backup, Report, Logging, Validation, Pagination, DI Container |
| 7. UI Integration | 7.1-7.4 | Merge PyQt6 UI + kết nối backend |
