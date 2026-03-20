# Requirements Document - Hệ Thống Quản Lý Phòng Trọ

## Introduction

Hệ thống quản lý phòng trọ là ứng dụng desktop được xây dựng bằng Python + PyQt6, sử dụng JSON/XML/XLSX để lưu trữ dữ liệu. Hệ thống hỗ trợ 2 loại người dùng: Admin (quản lý toàn bộ) và Guest (khách thuê phòng), với kiến trúc MVC và các tính năng đặc biệt như IoT Module giả lập và Contract Display.

## Glossary

- **System**: Hệ thống quản lý phòng trọ
- **Admin**: Người quản lý có toàn quyền trên hệ thống
- **Guest**: Khách thuê phòng với quyền hạn hạn chế (KHÔNG dùng "tenant")
- **Room**: Phòng trọ có thể cho thuê
- **Contract**: Hợp đồng thuê phòng giữa admin và guest
- **Invoice**: Hóa đơn thanh toán hàng tháng
- **Application**: Đơn đăng ký thuê phòng từ guest
- **Repair_Request**: Yêu cầu sửa chữa từ guest
- **Authentication_Service**: Dịch vụ xác thực người dùng
- **IoT_Module**: Module giả lập đọc số điện nước
- **Parser**: Bộ phân tích cú pháp dữ liệu (JSON/XML/XLSX)
- **Pretty_Printer**: Bộ định dạng xuất dữ liệu (JSON/XML/XLSX)

## Requirements

### Requirement 1: User Authentication

**User Story:** Là một người dùng, tôi muốn đăng nhập vào hệ thống, để có thể truy cập các chức năng phù hợp với vai trò của mình.

#### Acceptance Criteria

1. WHEN a user provides valid email/phone and password, THE Authentication_Service SHALL authenticate the user and grant access
2. WHEN a user provides invalid credentials, THE Authentication_Service SHALL return an authentication error message
3. THE System SHALL support two user roles: admin and guest
4. WHEN an admin logs in, THE System SHALL display the admin dashboard with full management capabilities
5. WHEN a guest logs in, THE System SHALL display appropriate interface based on their rental status

### Requirement 2: Guest Registration

**User Story:** Là một khách hàng mới, tôi muốn đăng ký tài khoản, để có thể sử dụng hệ thống thuê phòng.

#### Acceptance Criteria

1. WHEN a new user provides registration information, THE System SHALL create a guest account with role 'guest'
2. THE System SHALL validate email format and phone number format during registration
3. THE System SHALL hash passwords using bcrypt before storage
4. WHEN registration is successful, THE System SHALL allow immediate login with new credentials
5. THE System SHALL prevent duplicate accounts with same email or phone number

### Requirement 3: Room Management (Admin)

**User Story:** Là một admin, tôi muốn quản lý thông tin phòng trọ, để có thể cho thuê và theo dõi tình trạng phòng.

#### Acceptance Criteria

1. THE Admin SHALL create new rooms with room number, area, price, and amenities
2. THE Admin SHALL update existing room information including price and status
3. THE Admin SHALL delete rooms that are not currently under contract
4. WHEN a room is occupied, THE System SHALL prevent deletion of that room
5. THE System SHALL maintain room status as available, occupied, or maintenance
6. THE System SHALL store room data in JSON format for fast access
7. THE Admin SHALL filter rooms by status: đang thuê (occupied) or trống (available)

### Requirement 4: Guest Management (Admin)

**User Story:** Là một admin, tôi muốn quản lý thông tin khách thuê, để có thể theo dõi và liên lạc với họ.

#### Acceptance Criteria

1. THE Admin SHALL view all guest information including personal details and rental history
2. THE Admin SHALL update guest contact information when needed
3. THE Admin SHALL search guests by name, phone, or ID card number
4. THE System SHALL store guest data in XLSX format for tabular data management
5. WHEN a guest has active contracts, THE System SHALL display their current rental status
6. THE Admin SHALL filter guests by rental status: đang thuê (active), sắp hết hạn (expiring), or đã chấm dứt (terminated/expired)
7. THE Admin SHALL search guests by name

### Requirement 5: Room Browsing (Guest)

**User Story:** Là một guest, tôi muốn xem danh sách phòng trống, để có thể chọn phòng phù hợp với nhu cầu.

#### Acceptance Criteria

1. WHEN a guest without active rental logs in, THE System SHALL display available rooms list
2. THE System SHALL show room details including price, area, and amenities for each available room
3. THE Guest SHALL view detailed room information before making rental decision
4. THE System SHALL update room availability in real-time based on current contracts
5. THE System SHALL allow guests to filter rooms by price range and area

### Requirement 6: Rental Registration Process

**User Story:** Là một guest, tôi muốn đăng ký thuê phòng trống, để có thể thuê phòng ngay mà không cần chờ duyệt.

#### Acceptance Criteria

1. WHEN a guest selects an available room, THE System SHALL display rental registration form
2. THE System SHALL auto-fill guest personal information from user account
3. THE Guest SHALL provide additional information including ID card, occupation, and move-in date
4. WHEN registration is submitted, THE System SHALL automatically create a contract and update room status to occupied
5. THE System SHALL store rental registrations in XML format for hierarchical data structure
6. THE System SHALL prevent registration for rooms that are already occupied

### Requirement 7: Registration & Contract Oversight (Admin)

**User Story:** Là một admin, tôi muốn xem lịch sử đăng ký thuê phòng và quản lý hợp đồng, để có thể giám sát hoạt động cho thuê.

#### Acceptance Criteria

1. THE Admin SHALL view all rental registrations with guest and room details
2. THE Admin SHALL view registration history sorted by date
3. THE Admin SHALL terminate active contracts when needed, and THE System SHALL update room status to available
4. THE System SHALL prevent registration for already occupied rooms
5. THE Admin SHALL create contracts manually for walk-in guests

### Requirement 8: Contract Management

**User Story:** Là một admin, tôi muốn quản lý hợp đồng thuê phòng, để có thể theo dõi thời hạn và điều khoản thuê.

#### Acceptance Criteria

1. THE Admin SHALL create contracts manually or automatically from approved applications
2. THE System SHALL generate unique contract numbers with format HD[YYYY][MM][NNN]
3. THE Admin SHALL set contract duration, monthly rent, and deposit amount
4. THE System SHALL track contract status as active, expired, or terminated
5. THE System SHALL store contract data in XML format for complex document structure
6. WHEN a contract expires, THE System SHALL automatically update room status to available

### Requirement 9: Contract Display and Export

**User Story:** Là một admin, tôi muốn hiển thị và xuất hợp đồng, để có thể in và lưu trữ tài liệu.

#### Acceptance Criteria

1. THE System SHALL display contracts using HTML templates for formatted presentation
2. THE System SHALL export contracts to PDF format for printing and archival
3. THE Pretty_Printer SHALL format contract data into readable HTML layout
4. FOR ALL valid contracts, THE System SHALL generate consistent PDF output from HTML template
5. THE System SHALL include all contract details, guest information, and terms in exported documents

### Requirement 10: Invoice Generation

**User Story:** Là một admin, tôi muốn bấm nút tạo hóa đơn hàng tháng tại mục quản lý phòng, để hệ thống tự kết nối IoT ghi nhận điện nước rồi tạo hóa đơn cho tất cả phòng đang thuê.

#### Acceptance Criteria

1. THE Admin SHALL have a "Tạo hóa đơn hàng tháng" button in the room management section (quản lý phòng)
2. WHEN the button is pressed, THE System SHALL automatically connect to IoT Module and record electricity and water readings for all rooms under active contracts
3. AFTER recording readings, THE System SHALL generate monthly invoices for all active contracts
4. THE System SHALL calculate total amount including rent, utilities (from IoT readings), and additional fees
5. THE System SHALL generate unique invoice numbers with format INV[YYYY][MM][NNN]
6. THE System SHALL store invoice data in XLSX format for financial reporting
7. WHEN invoice is created, THE System SHALL set due date as 5 days from generation date

### Requirement 11: IoT Module Integration

**User Story:** Là một admin, tôi muốn hệ thống tự động đọc số điện nước, để có thể tính toán hóa đơn chính xác.

#### Acceptance Criteria

1. THE IoT_Module SHALL simulate automatic reading of electricity and water meters
2. WHEN end of month occurs, THE IoT_Module SHALL provide current meter readings for all rooms
3. THE System SHALL calculate utility consumption based on previous and current readings
4. THE System SHALL apply configurable rates for electricity and water usage
5. IF IoT_Module fails to provide readings, THE System SHALL allow manual input with admin override

### Requirement 12: Payment Tracking

**User Story:** Là một admin, tôi muốn theo dõi thanh toán hóa đơn, để có thể quản lý tài chính hiệu quả.

#### Acceptance Criteria

1. THE Admin SHALL mark invoices as paid when payment is received
2. THE System SHALL track payment date and method for each invoice
3. THE System SHALL generate overdue notices for unpaid invoices past due date
4. THE System SHALL calculate total revenue and outstanding amounts for reporting
5. THE System SHALL maintain payment history for each guest
6. THE Admin SHALL filter invoices by month/year and by payment status (đã thanh toán / chưa thanh toán)

### Requirement 13: Guest Invoice Access

**User Story:** Là một guest, tôi muốn xem hóa đơn của mình, để có thể biết số tiền cần thanh toán.

#### Acceptance Criteria

1. WHEN a guest with active rental logs in, THE System SHALL display their current and past invoices
2. THE Guest SHALL view invoice details including breakdown of charges
3. THE System SHALL show payment status and due dates for each invoice
4. THE Guest SHALL access payment history for their rental period
5. THE System SHALL restrict guests to view only their own invoices

### Requirement 14: Repair Request Management

**User Story:** Là một guest, tôi muốn gửi yêu cầu sửa chữa, để có thể báo cáo vấn đề trong phòng.

#### Acceptance Criteria

1. THE Guest SHALL submit repair requests with description and priority level
2. THE System SHALL assign unique request numbers and timestamps to each request
3. THE Admin SHALL view all repair requests with guest and room information
4. THE Admin SHALL update request status as pending, in-progress, or completed
5. THE System SHALL store repair requests in XML format for structured data management
6. THE Guest SHALL view status updates for their submitted requests

### Requirement 15: Data Storage and Parsing

**User Story:** Là một developer, tôi muốn hệ thống xử lý dữ liệu đáng tin cậy, để đảm bảo tính toàn vẹn thông tin.

#### Acceptance Criteria

1. THE Parser SHALL parse JSON files for user and room data with error handling
2. THE Parser SHALL parse XML files for contract and repair request data with validation
3. THE Parser SHALL parse XLSX files for guest and invoice data with type checking
4. THE Pretty_Printer SHALL format data back to valid JSON, XML, and XLSX formats
5. FOR ALL valid data objects, parsing then printing then parsing SHALL produce equivalent objects (round-trip property)
6. WHEN invalid data format is encountered, THE Parser SHALL return descriptive error messages

### Requirement 16: Data Backup and Recovery

**User Story:** Là một admin, tôi muốn sao lưu dữ liệu hệ thống, để có thể khôi phục khi cần thiết.

#### Acceptance Criteria

1. THE System SHALL create automatic daily backups of all data files
2. THE Admin SHALL manually trigger backup creation at any time
3. THE System SHALL maintain backup files for at least 30 days
4. THE Admin SHALL restore system data from any available backup
5. WHEN restore is performed, THE System SHALL validate data integrity before applying changes

### Requirement 17: System Configuration

**User Story:** Là một admin, tôi muốn cấu hình các thông số hệ thống, để có thể tùy chỉnh theo nhu cầu quản lý.

#### Acceptance Criteria

1. THE Admin SHALL configure electricity and water rates for utility calculations
2. THE Admin SHALL set default contract duration and deposit requirements
3. THE Admin SHALL customize invoice due date periods
4. THE System SHALL store configuration in JSON format for easy modification
5. WHEN configuration changes are made, THE System SHALL apply them immediately to new transactions

### Requirement 18: Reporting and Statistics

**User Story:** Là một admin, tôi muốn xem báo cáo và thống kê, để có thể đánh giá hiệu quả kinh doanh.

#### Acceptance Criteria

1. THE System SHALL generate monthly revenue reports with payment summaries
2. THE System SHALL show room occupancy statistics and trends
3. THE System SHALL display guest retention and turnover rates
4. THE Admin SHALL export reports to PDF and Excel formats
5. THE System SHALL provide dashboard with key performance indicators

### Requirement 19: Security and Access Control

**User Story:** Là một system administrator, tôi muốn hệ thống bảo mật, để bảo vệ thông tin khách hàng và dữ liệu kinh doanh.

#### Acceptance Criteria

1. THE System SHALL encrypt all password data using bcrypt hashing
2. THE System SHALL implement role-based access control for admin and guest functions
3. THE System SHALL log all user actions for audit trail
4. THE System SHALL automatically log out users after period of inactivity
5. THE System SHALL validate all input data to prevent injection attacks

### Requirement 20: User Interface Responsiveness

**User Story:** Là một người dùng, tôi muốn giao diện phản hồi nhanh, để có thể làm việc hiệu quả.

#### Acceptance Criteria

1. THE System SHALL load main dashboard within 3 seconds of login
2. THE System SHALL respond to user actions within 1 second for local operations
3. THE System SHALL display loading indicators for operations taking longer than 2 seconds
4. THE System SHALL maintain responsive interface during data processing
5. WHEN large datasets are loaded, THE System SHALL implement pagination to maintain performance
