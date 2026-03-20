# UI Integration

Folder dự phòng cho UI assets khi cần merge UI design riêng vào project.

Trong workflow hiện tại, UI được implement trực tiếp trong Phase 7 của `tasks.md` (folder `ui/` trong project structure). Folder này chỉ cần dùng nếu UI design được cung cấp từ nguồn bên ngoài (Figma export, designer handoff, etc.).

## Cách sử dụng (nếu cần)

1. Copy UI assets (images, icons, stylesheets) vào đây
2. Tạo file `ui-backend-mapping.md` để map UI components với backend services
3. Follow Phase 7 trong `tasks.md` để integrate
