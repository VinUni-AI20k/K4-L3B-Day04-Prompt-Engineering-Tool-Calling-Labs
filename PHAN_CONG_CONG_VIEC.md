# Phân công công việc nhóm — Day04

## 1. Mục tiêu chung

Hoàn thiện trợ lý AI theo lĩnh vực đã chốt, có khả năng chọn đúng tool, truyền đúng input, hỏi lại khi thiếu thông tin, xử lý hội thoại nhiều lượt, xác nhận/hủy hành động ghi dữ liệu và bảo vệ dữ liệu nội bộ.

Phạm vi mặc định của kế hoạch này là giữ format **IT Helpdesk** có sẵn. Nếu nhóm đổi lĩnh vực, cần chốt lại luồng chính, bộ 30 case cơ bản và bộ 12 case an toàn trước khi chạy v0; các đầu việc và tiêu chí evidence bên dưới vẫn giữ nguyên.

### Quy tắc không được quên

- Không sửa các bộ case cố định để làm tăng điểm: `starter_v0/data/eval_base.json`, `eval_adversarial.json`, `eval_helpdesk_extension.json`.
- `eval_group.json` phải có đúng **10 case tự viết**: 5 single-turn và 5 multi-turn; không sao chép các ví dụ trong `samples/`.
- Run chỉ được dùng làm evidence khi `provider_error_cases == 0` và `measured_cases == total_cases`; phải đọc cả `tool_results`/error, không chỉ nhìn routing PASS.
- Không commit `.env`, API key, token, mật khẩu, OTP, recovery code, dữ liệu thật, `.venv`, cache hoặc ticket phát sinh.
- Mọi thành viên phải có ít nhất một commit kỹ thuật và tự viết mục `INDIVIDUAL` trong `TEAM.md`.
- Hành động ghi dữ liệu như `create_ticket` chỉ được thực hiện sau khi người dùng xác nhận rõ đúng nội dung.

## 2. Phân công cho 5 thành viên

Tên đang để dạng `Thành viên 1–5`; nhóm thay bằng họ tên, MSSV và GitHub trong `TEAM.md`.

| Thành viên | Vai trò chính | File/khu vực phụ trách | Sản phẩm bàn giao |
|---|---|---|---|
| **Thành viên 1** | Trưởng nhóm, tích hợp và checkout | `TEAM.md`, `starter_v0/artifacts/REPORT.md`, cấu hình repo và tích hợp toàn bộ branch | Luồng cơ bản đã chốt, repo chạy được, report hoàn chỉnh, bảng kiểm tra cuối, link nộp VLearn |
| **Thành viên 2** | Prompt engineering và tool declaration | `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`, các `TOOL.md` liên quan | Phân tích lỗi prompt/tool, hypothesis và các thay đổi v1–v3; kiểm tra tên tool/tham số khớp registry |
| **Thành viên 3** | Evaluation và version evidence | `starter_v0/run_eval.py`, `scripts/parse_runs.py`, `artifacts/version_log.csv`, thư mục `runs/`, `analysis/` | Chạy v0–v3 cùng provider/model/bộ case, ghi metric và đường dẫn run, so sánh trước/sau |
| **Thành viên 4** | Team eval và safety | `starter_v0/data/eval_group.json`, run suite `group`/`adversarial`, `company_policy/`, phân tích safety | 5 case single-turn + 5 case multi-turn, run 12 case safety, phân tích sâu ít nhất 3 case và kiểm tra dữ liệu nhạy cảm |
| **Thành viên 5** | UI chat và transcript/demo | `starter_v0/chat.py` và giao diện liên quan, `transcripts/`, kịch bản demo | UI hiển thị version, tool call, input, kết quả/lỗi; transcript của các luồng bình thường, thiếu thông tin, nhiều lượt và tạo ticket |

## 3. Phụ thuộc và thứ tự bàn giao

Các thành viên có thể bắt đầu một số việc song song, nhưng cần giữ thứ tự bàn giao sau để tránh chạy sai version hoặc thiếu evidence:

```text
TV1 chốt lĩnh vực/provider/luồng chính
        ↓
TV3 chạy baseline v0 và phân tích lỗi
        ↓
TV2 sửa system_prompt.md/tools.yaml, tạo v1–v3
        ↓
TV3 chạy eval v1–v3 và cập nhật version_log.csv
        ↓
TV4 chạy group/adversarial       TV5 hoàn thiện UI/transcript cuối
                 \                 /
                  ↓               ↓
             TV1 tích hợp report, TEAM và checkout
```

### Output bắt buộc trước khi chuyển việc

| Bước | Người bàn giao | Output tối thiểu | Người nhận/sử dụng |
|---|---|---|---|
| 1 | **TV1** | Lĩnh vực, người dùng, luồng cơ bản, provider/model và repo đã chốt trong `TEAM.md` | Tất cả thành viên |
| 2 | **TV3** | Run v0 của base 30 case, có metric và danh sách failure thực tế | TV2 để đặt hypothesis sửa prompt/tool |
| 3 | **TV2** | Các bản thay đổi v1–v3 của `system_prompt.md`/`tools.yaml`, kèm hypothesis | TV3 chạy eval; TV4 review boundary; TV5 test artifact |
| 4 | **TV4** | `data/eval_group.json` đúng 5 single-turn + 5 multi-turn | TV3 chạy suite `group` |
| 5 | **TV3** | Run v1–v3, run group/adversarial, `version_log.csv`, bảng so sánh trước/sau | TV1 viết report; TV4 đối chiếu safety |
| 6 | **TV5** | UI chạy được và transcript chính thức có version, tool call, args, tool result/error | TV1 đưa vào report và demo |
| 7 | **TV1** | Report, TEAM, checklist và branch cuối đã tích hợp | Cả nhóm kiểm tra trước khi nộp |

### Việc có thể làm song song

- **TV2** có thể đọc baseline và chuẩn bị các giả thuyết trong lúc **TV3** đang chạy v0, nhưng chỉ chốt thay đổi dựa trên failure thực tế.
- **TV4** có thể thiết kế nháp 10 case và safety checklist từ CP0; chỉ chạy bộ case sau khi dataset đã được kiểm tra schema và artifact cần test đã chốt.
- **TV5** có thể kiểm tra cấu trúc `chat.py` và làm UI nền từ CP0; transcript dùng làm evidence cuối nên chạy lại sau artifact v3.
- **TV1** theo dõi blocker và chuẩn bị khung report xuyên suốt; chỉ hoàn thiện kết luận/checkout sau khi nhận đủ run, transcript và commit của các thành viên.

### Điểm chặn cần báo ngay

- Chưa chốt provider/model hoặc preflight lỗi: chưa thể coi run v0 là evidence.
- Run có `provider_error_cases > 0` hoặc `measured_cases < total_cases`: TV3 phải xử lý môi trường/provider trước khi gửi metric cho TV1.
- `tools.yaml` không khớp implementation: TV2 sửa trước khi TV3 chạy version tiếp theo.
- `eval_group.json` sai schema hoặc thiếu 5+5 case: TV4 sửa trước khi TV3 chạy suite group.
- Transcript không có tool result/error hoặc có dữ liệu nhạy cảm: TV5 phải tạo lại và TV1 chưa đưa vào report.

## 4. Chi tiết đầu việc và tiêu chí hoàn thành

### Thành viên 1 — Trưởng nhóm, tích hợp và checkout

1. Đầu buổi chốt trong `TEAM.md`:
   - lĩnh vực và người dùng mục tiêu;
   - một nhiệm vụ/luồng cơ bản;
   - provider/model dùng chung;
   - tên repo đúng mẫu `K4-L3-DAY04-HoVaTen-MSSV-PromptEngineeringToolCalling`.
2. Kiểm tra môi trường, quyền repo và preflight provider; hỗ trợ thành viên gặp lỗi cài đặt.
3. Theo dõi dependency giữa các phần: Thành viên 2 sửa artifact, Thành viên 3 chạy eval, Thành viên 4/5 tạo evidence, sau đó tích hợp vào `REPORT.md`.
4. Hoàn thiện các phần của report: giới thiệu agent, capability/giới hạn, link run/transcript, tổng hợp kết quả, giới hạn còn lại và reflection.
5. Hoàn thiện bảng thành viên, vai trò, file/commit/PR và phần nhận xét chung trong `TEAM.md`.
6. Trước khi nộp, kiểm tra branch cuối, lịch sử commit của cả 5 người, URL repo và checklist trong `SUBMISSION.md`.

**Tiêu chí bàn giao:** repo clone được; README hướng dẫn chạy đúng; report dẫn tới evidence thật; không có secret/dữ liệu cấm; 5 mục `INDIVIDUAL` đã được từng người tự viết.

### Thành viên 2 — Prompt engineering và tool declaration

1. Đọc baseline trong `system_prompt.md`, `tools.yaml`, `tools/README.md` và các `TOOL.md` cần thiết; đối chiếu với implementation trong `tools/`.
2. Từ lỗi v0 do Thành viên 3 cung cấp, phân loại lỗi: `wrong_tool`, `wrong_arg_value`, `missing_info`, `wrong_boundary`, `unnecessary_tool` hoặc `out_of_scope`.
3. Đề xuất hypothesis có thể kiểm chứng, ví dụ:
   - prompt nêu rõ khi nào dùng/không dùng từng tool;
   - schema mô tả rõ ý nghĩa và giá trị hợp lệ của tham số;
   - bắt buộc hỏi lại khi thiếu định danh hoặc phải xác nhận trước hành động ghi dữ liệu;
   - cấm gửi asset ID, employee ID, hostname, serial, vị trí hoặc chẩn đoán nội bộ ra tra cứu web.
4. Thực hiện các thay đổi có kiểm soát cho v1, v2, v3; mỗi vòng nên thay đổi một phần chính và ghi lý do.
5. Kiểm tra `tools.yaml` khớp tên hàm, tham số và implementation; không để case expect gọi tool không tồn tại.

**Tiêu chí bàn giao:** bản artifact cuối rõ ràng, nhất quán với tool registry; có bảng hypothesis/change để Thành viên 3 đưa vào `version_log.csv`; không thay đổi bộ case cố định.

### Thành viên 3 — Evaluation và version evidence

1. Chạy v0 khi chưa sửa artifact, lưu JSON vào `starter_v0/runs/`.
2. Sau mỗi vòng thay đổi, chạy v1, v2, v3 với cùng provider/model và cùng bộ base 30 case. Ghi artifact hash/version, metric và đường dẫn file.
3. Lệnh mẫu:

   ```powershell
   cd starter_v0
   python scripts/preflight_provider.py --provider openrouter
   python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json
   python run_eval.py --provider openrouter --version v1 --suite base --eval-cases data/eval_base.json
   python run_eval.py --provider openrouter --version v2 --suite base --eval-cases data/eval_base.json
   python run_eval.py --provider openrouter --version v3 --suite base --eval-cases data/eval_base.json
   ```

   Thay `openrouter` bằng provider nhóm đã chốt; nếu dùng model riêng thì thêm `--model <model>`.
4. Cập nhật `starter_v0/artifacts/version_log.csv` cho từng version: thời điểm, hypothesis, thay đổi, provider/model, metric, run file và ghi chú lỗi.
5. Đọc thủ công các case fail và `tool_results`, phân biệt routing đúng với tool thực thi thành công; không tự biến provider error thành FAIL logic.
6. Khi Thành viên 4 hoàn thiện dataset nhóm, chạy thêm suite `group`; chạy `adversarial` cho 12 case và lưu run.

**Tiêu chí bàn giao:** có đủ run v0/v1/v2/v3, `provider_error_cases == 0`, `measured_cases == total_cases`, version log truy ngược được tới file run và bảng so sánh trước/sau cho report.

### Thành viên 4 — Team eval và safety

1. Thiết kế `starter_v0/data/eval_group.json` đúng schema hiện có.
2. Viết đúng 10 case mới:
   - 5 single-turn kiểm tra chọn tool, giá trị tham số, thiếu thông tin hoặc out-of-scope;
   - 5 multi-turn kiểm tra sửa yêu cầu, hủy, xác nhận, bối cảnh hội thoại và không gọi tool thừa.
3. Mỗi case phải có `id`, `phase: "B"`, `failure_type`, input/query hoặc `turns`, `expect` và `metadata.what_it_tests`.
4. Chạy bộ 10 case bằng `--suite group --eval-cases data/eval_group.json`; không sửa expectation sau khi đã thấy kết quả để tăng điểm.
5. Chạy `eval_adversarial.json` bằng suite `adversarial`; phân tích ít nhất 3 case trong mục `B4a` của report.
6. Với mỗi case safety, kiểm tra cả actual tool calls, args, `tool_results` và filesystem/ticket output; xác nhận không có exfiltration dữ liệu nội bộ và không có hành động ghi dữ liệu khi chưa được xác nhận.

**Tiêu chí bàn giao:** file group có đủ 5+5 case, run group/adversarial thật, bảng phân tích 3 case trở lên, kết luận safety dựa trên trace chứ không chỉ PASS/FAIL.

### Thành viên 5 — UI chat và transcript/demo

1. Kiểm tra cách chạy `starter_v0/chat.py`; giữ agent loop/provider hoạt động ổn định.
2. Hoàn thiện UI chat để người dùng/chấm bài thấy được:
   - version artifact đang chạy;
   - user message và assistant response;
   - tên tool và input/args;
   - kết quả thành công hoặc lỗi từ tool;
   - trạng thái hỏi lại, chờ người dùng, hủy hoặc dừng do lỗi.
3. Tạo transcript thật cho tối thiểu các tình huống:
   - yêu cầu bình thường như kiểm tra VPN hoặc trạng thái service;
   - thiếu thông tin cần hỏi lại;
   - hội thoại nhiều lượt có sửa/hủy yêu cầu;
   - hành động `create_ticket` chỉ sau xác nhận rõ.
4. Kiểm tra transcript trước khi commit để chắc chắn không chứa key, token, mật khẩu, OTP, dữ liệu thật hoặc ticket phát sinh ngoài ý muốn.
5. Bàn giao 3–5 scenario demo cho Thành viên 1 đưa vào bảng A4/B4 của report, kèm đường dẫn transcript và tool trace.

**Tiêu chí bàn giao:** thành viên khác có thể chạy UI theo README; UI không che tool error; transcript ghi được version, input, tool call, args, tool result và outcome.

## 5. Lịch phối hợp theo checkpoint

| Mốc | Thành viên 1 | Thành viên 2 | Thành viên 3 | Thành viên 4 | Thành viên 5 |
|---|---|---|---|---|---|
| **CP0 — 17:50–18:00** | Chốt lĩnh vực, repo, TEAM | Đọc artifact và registry | Cài môi trường, preflight | Đọc schema/policy, lên ý tưởng case | Kiểm tra luồng chat và cách lưu transcript |
| **CP1 — 18:00–18:20** | Theo dõi blocker | Phân tích baseline prompt/tool | Chạy v0 base 30 case | Soạn nháp 10 case và safety checklist | Xác định các scenario cần demo |
| **CP2 — 18:20–19:05** | Review tích hợp | Sửa prompt/tool theo từng hypothesis | Chạy v1–v3, cập nhật version log | Review boundary sau mỗi version | Test nhanh UI theo artifact mới |
| **CP3 — 19:05–19:30** | Kiểm tra evidence | Sửa lỗi prompt nếu safety phát hiện | Chạy suite safety và lưu run | Chốt group 5+5, chạy adversarial, phân tích 3 case | Tạo transcript thiếu thông tin/xác nhận/hủy |
| **CP4 — 19:30–20:10** | Ghép report và link file | Review consistency với report | Kiểm tra metric/run paths | Kiểm tra dataset và safety evidence | Hoàn thiện UI, transcript và demo flow |
| **FINAL — 20:10–20:25** | Merge/review/checklist | Commit artifact cuối | Commit evidence/version log | Commit eval/analyse | Commit UI/transcript |
| **DEMO — 20:25–21:00** | Điều phối trình bày | Giải thích hypothesis/fix | Mở metric/run | Trình bày safety/team case | Chạy UI và chỉ ra tool trace |

## 6. Quy ước commit và bàn giao

- Mỗi người làm trên branch riêng hoặc commit có prefix rõ: `prompt:`, `eval:`, `safety:`, `ui:`, `report:`.
- Mỗi bàn giao gửi trong nhóm: file đã đổi, commit hash, cách kiểm tra, vấn đề còn lại.
- Thành viên 1 chỉ tích hợp sau khi người phụ trách tự chạy kiểm tra và ghi evidence; không force-push, không xóa commit, không sửa lịch sử để che thay đổi muộn.
- Sau khi merge, mỗi người tự cập nhật và commit mục `INDIVIDUAL` trong `TEAM.md`, gồm phần việc/file/commit, quyết định hoặc khó khăn, điều đã học, AI/công cụ đã dùng và cách kiểm tra.

## 7. Checklist cuối nhóm

- [ ] `TEAM.md` có đủ 5 thành viên, MSSV, GitHub, vai trò, file/commit/PR.
- [ ] Có đủ run base v0–v3, `version_log.csv`, hypothesis và so sánh trước/sau.
- [ ] `eval_group.json` có đúng 5 single-turn + 5 multi-turn; có run group.
- [ ] Có run 12 case adversarial và phân tích ít nhất 3 case dựa trên trace.
- [ ] `system_prompt.md` và `tools.yaml` khớp tool registry/implementation.
- [ ] UI hiển thị version, tool call, input, kết quả/lỗi; có transcript của các luồng bắt buộc.
- [ ] `starter_v0/artifacts/REPORT.md` có đầy đủ cách chạy, evidence, giới hạn và link thật.
- [ ] Không có `.env`, secret, dữ liệu thật, `.venv`, cache hoặc generated ticket.
- [ ] Mỗi thành viên có commit kỹ thuật và mục `INDIVIDUAL` riêng.
- [ ] Mọi thành viên nộp cùng một URL repo nhóm trên VLearn trước deadline áp dụng.
