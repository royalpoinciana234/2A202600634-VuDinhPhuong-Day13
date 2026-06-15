# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- GROUP_NAME: 2A202600634-VuDinhPhuong-Day13
- REPO_URL: https://github.com/VuDinhPhuong/2A202600634-VuDinhPhuong-Day13
- MEMBERS:
  - Member A: Vu Dinh Phuong | Role: Logging, PII, Tracing, SLOs, Alerts & Dashboard (Sole Developer)

---

## 2. Group Performance (Auto-Verified)
- VALIDATE_LOGS_FINAL_SCORE: 100/100
- TOTAL_TRACES_COUNT: 20
- PII_LEAKS_FOUND: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- EVIDENCE_CORRELATION_ID_SCREENSHOT: docs/images/EVIDENCE_CORRELATION_ID_SCREENSHOT.png
- EVIDENCE_PII_REDACTION_SCREENSHOT: docs/images/EVIDENCE_PII_REDACTION_SCREENSHOT.png
- EVIDENCE_TRACE_WATERFALL_SCREENSHOT: docs/images/EVIDENCE_TRACE_WATERFALL_SCREENSHOT.png
- TRACE_WATERFALL_EXPLANATION: Span `run` tương ứng với quá trình xử lý của phương thức `LabAgent.run` với tin nhắn đầu vào `"How should alerts be designed?"`. Điểm thú vị nhất là tổng thời gian thực thi (latency) kéo dài đúng **2650ms**. Điều này xảy ra do sự cố giả lập `rag_slow` đang được kích hoạt, khiến tác vụ tìm kiếm RAG (`retrieve()`) bị trì hoãn mất **2.5 giây** (`time.sleep(2.5)`), và thời gian thực tế để LLM sinh câu trả lời chỉ mất khoảng **150ms** (`2500ms + 150ms = 2650ms`). Toàn bộ metadata bao gồm token sử dụng (29 In, 136 Out), chi phí ($0.002127) và điểm chất lượng chất lượng (0.9) đều được tự động lưu vết chính xác kèm theo trace ID `d6dfb399-...`.

### 3.2 Dashboard & SLOs
- DASHBOARD_6_PANELS_SCREENSHOT: docs/images/DASHBOARD_6_PANELS_SCREENSHOT_1.png
- SLO_TABLE:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 2650.0 ms |
| Error Rate | < 2% | 28d | 0.00% |
| Cost Budget | < $2.5/day | 1d | $0.1884 |

### 3.3 Alerts & Runbook
- ALERT_RULES_SCREENSHOT: docs/images/ALERT_RULES_SCREENSHOT_1.png
- SAMPLE_RUNBOOK_LINK: docs/images/ALERT_RULES_SCREENSHOT_2.png

---

## 4. Incident Response (Group)
- SCENARIO_NAME: tool_fail
- SYMPTOMS_OBSERVED: Hệ thống API chat trả về mã lỗi HTTP 500 liên tiếp. Giao diện Live Dashboard ghi nhận tỉ lệ lỗi tăng vọt lên **12.50%** (vượt xa ngưỡng SLO cho phép là **< 2%**).
- ROOT_CAUSE_PROVED_BY: Trace ID sự cố trên Langfuse: `req-0bf26036` (hoặc log lỗi event: `request_failed` với chi tiết `RuntimeError: Vector store timeout`).
- FIX_ACTION: Gọi API vô hiệu hóa kịch bản giả lập sự cố thông qua lệnh: `curl -X POST http://127.0.0.1:8000/incidents/tool_fail/disable`.
- PREVENTIVE_MEASURE: Cấu hình cơ chế ngắt mạch (Circuit Breaker) cho tầng kết nối RAG. Khi kết nối timeout, hệ thống tự động fallback sử dụng tập tài liệu/câu trả lời tĩnh cố định để đảm bảo dịch vụ không bị gián đoạn và không trả về lỗi 500 cho người dùng.

---

## 5. Individual Contributions & Evidence

### Vu Dinh Phuong
- TASKS_COMPLETED: 
  1. Triển khai Middleware quản lý Correlation ID (app/middleware.py) giúp tự động trích xuất, khởi tạo mã ID định dạng `req-xxxxxxxx` và đính kèm thông tin thời gian xử lý `x-response-time-ms` vào Header phản hồi.
  2. Xây dựng bộ lọc làm sạch dữ liệu nhạy cảm PII dạng đệ quy (app/logging_config.py & app/pii.py) giúp rà soát toàn bộ cấu trúc log JSON và mã hóa/redact các thông tin cá nhân như Email, Số điện thoại Việt Nam, Số thẻ tín dụng, Số CCCD.
  3. Tích hợp SDK Langfuse Tracing và sử dụng decorator `@observe` (app/agent.py) để tự động ghi vết (trace) các spans và metadata (tokens, costs, quality score, tags).
  4. Thiết kế và triển khai trang Live Dashboard quan sát thời gian thực (app/dashboard.html) tích hợp các biểu đồ Chart.js trực quan với đường SLO line chỉ báo ngưỡng cảnh báo, hỗ trợ khôi phục dữ liệu từ log khi restart server.
  5. Cấu hình và kiểm thử các luật cảnh báo SLO (config/alert_rules.yaml) cho các trường hợp Latency P95, Error Rate, và Cost Budget.
- EVIDENCE_LINK: https://github.com/VuDinhPhuong/2A202600634-VuDinhPhuong-Day13/docs/images
