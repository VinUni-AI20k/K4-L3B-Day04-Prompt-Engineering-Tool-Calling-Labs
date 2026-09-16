# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: Vinno
- Người đại diện / MSSV: Trịnh Quốc Hoàng / 2A202602847
- Tên repo: `K4B-Day4-Vinno`
- URL repo, nhánh nộp, commit chốt: https://github.com/hoang-trinh/K4B-Day4-Vinno
- Deadline áp dụng và link thông báo đổi hạn nếu có:

## Thành viên

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
| Vũ Minh Trí | 2A202602629 | akari-zero-1 | Sửa prompt/tool để xử lý 9 lỗi v0. Chạy v1–v3 và ghi version log. UI/transcript. | system_prompt.md, tools.yaml, version_log.csv, v1-v3...json, wed_ui.py|
| Trịnh Quốc Hoàng | 2A202602847 | hoang-trinh | Sửa prompt/tool để xử lý 9 lỗi v0. Chạy v1–v3 và ghi version log. Chạy adversarial. | system_prompt.md, tools.yaml, version_log.csv, v1-v3...json|
| Dương Đình Long | 2A202602474 | DLongg | Sửa prompt/tool để xử lý 9 lỗi v0. Chạy v1–v3 và ghi version log. Chạy adversarial. Viết 10 case nhóm. | system_prompt.md, tools.yaml, version_log.csv, v1-v3...json, eval_group.json |
| Vũ Tiến Linh | 2A202602657 | Linh-Huong | Sửa prompt/tool để xử lý 9 lỗi v0. Chạy v1–v3 và ghi version log. Chạy adversarial. Hoàn thiện report, TEAM và kiểm tra submission. | system_prompt.md, tools.yaml, version_log.csv, v1-v3...json, REPORT.md|
## Nhận xét chung

- Kết quả và bằng chứng: Nhóm đã hoàn thành việc sửa 9 lỗi ở phiên bản v0, chạy các phiên bản v1–v3 trên bộ dữ liệu base, adversarial, group và extension, đồng thời cập nhật version log và lưu các run/transcript trong thư mục starter_v0/runs. Bằng chứng rõ nhất là các file system_prompt.md, tools.yaml, version_log.csv và các JSON run đã được cập nhật theo từng vòng đánh giá.
- Thay đổi hiệu quả nhất: Việc chỉnh sửa prompt và tool definition để làm rõ policy, logic xử lý permission/tool use, và cách quản lý incident/response đã giúp agent ổn định hơn ở các vòng chạy sau. Đây là phần thay đổi đã mang lại cải thiện rõ nhất trong hiệu suất và độ nhất quán của hệ thống.
- Giới hạn còn lại: Một số trường hợp edge case và dữ liệu adversarial vẫn cần kiểm tra thêm ở quy mô lớn hơn, vì các mô hình AI vẫn có thể mắc sai lầm khi gặp yêu cầu mơ hồ, nhiều bước hoặc cần liên kết thông tin từ nhiều nguồn cùng lúc.
- Cách phân công và tích hợp: Nhóm chia theo mảng rõ ràng: sửa prompt/tool, chạy benchmark và ghi log, xây dựng test case nhóm, hỗ trợ UI/transcript, và hoàn thiện báo cáo/submission. Các thay đổi được tích hợp trên repo chung, kiểm tra lại bằng run_eval, transcript và log để đảm bảo tính nhất quán trước khi nộp.

## INDIVIDUAL

### Vũ Minh Trí — 2A202602629

- Phần việc và file/commit/PR: Làm phần sửa prompt/tool để xử lý 9 lỗi v0, cập nhật version log và chạy các vòng v1–v3; hỗ trợ UI/transcript cho quá trình đánh giá và kiểm tra mô hình. File chính: system_prompt.md, tools.yaml, version_log.csv, các run JSON trong starter_v0/runs và file UI/transcript liên quan.
- Quyết định, khó khăn và cách xử lý: Tôi tập trung vào việc làm rõ hướng dẫn của agent và định nghĩa tool để giảm lỗi lặp lại ở các lượt chạy. Khó khăn lớn nhất là khớp giữa prompt/tool với yêu cầu thực tế của từng case; tôi đã rà soát transcript, log và output chạy lại để chỉnh sửa từng điểm cụ thể.
- Điều đã học: Từ dự án này, tôi hiểu rõ hơn rằng hiệu quả của AI agent không chỉ phụ thuộc vào model mà còn phụ thuộc rất lớn vào prompt, policy, định nghĩa tool và cách kiểm tra bằng log/transcript. Việc đánh giá cần được thực hiện theo từng vòng để nhìn ra nguyên nhân gốc rễ.
- AI/công cụ đã dùng và cách kiểm tra: Github Copilot, VS Code, terminal Python, script run_eval và đọc log/transcript để đối chiếu đầu ra. Tôi kiểm tra bằng cách chạy lại các case và so sánh output với tiêu chí lỗi trước/sau.
- Thời điểm đã tự nộp URL repo chung trên VLearn: 16/09/2026

### Trịnh Quốc Hoàng — 2A202602847

- Phần việc và file/commit/PR: Tham gia sửa prompt/tool để xử lý 9 lỗi v0, chạy các phiên bản v1–v3 và cập nhật version log. Đồng thời hỗ trợ chạy adversarial để kiểm tra khả năng chịu đựng của agent trước các tình huống bất lợi và không chuẩn.
- Quyết định, khó khăn và cách xử lý: Tôi ưu tiên sửa các lỗi có tính lặp lại và ảnh hưởng trực tiếp đến độ tin cậy của agent. Khi có sai lệch giữa các run, tôi kiểm tra lại lý do dựa trên prompt/tool và log output để tìm điểm thay đổi hiệu quả nhất thay vì sửa bừa.
- Điều đã học: Tôi nhận ra rằng việc làm tốt prompt không chỉ là viết rõ ràng hơn mà còn phải đồng bộ với định nghĩa tool, policy và phản hồi thực tế của hệ thống. Quá trình chạy benchmark giúp xác định bản chất lỗi thay vì chỉ sửa bề mặt.
- AI/công cụ đã dùng và cách kiểm tra: GitHub Copilot, VS Code, các script chạy đánh giá và đọc file JSON run để đối chiếu. Tôi kiểm tra bằng cách so sánh kết quả từ các phiên bản v1-v3 và các lỗi adversarial để xác nhận mức cải thiện.
- Thời điểm đã tự nộp URL repo chung trên VLearn: 16/09/2026

### Dương Đình Long — 2A202602474

- Phần việc và file/commit/PR: Viết và kiểm tra 10 case nhóm, đồng thời tham gia sửa prompt/tool cho 9 lỗi v0, chạy v1–v3 và cập nhật version log. Bên cạnh đó, hỗ trợ kiểm tra các trường hợp group/adversarial để đánh giá độ bền của agent.
- Quyết định, khó khăn và cách xử lý: Tôi quyết định xây dựng các case nhóm theo hướng mô phỏng tình huống thực tế để đánh giá mức độ xử lý đa bước, quyền truy cập và các quy tắc an toàn. Khó khăn lớn là giữ cho case đủ sát thực tế nhưng không phá vỡ tiêu chí kiểm tra; tôi đã rà soát lại từng case và điều chỉnh dựa trên output thực tế.
- Điều đã học: Tôi học được cách đánh giá AI bằng các tình huống thực tế chứ không chỉ dựa trên một vài prompt mẫu. Việc thêm case nhóm giúp phát hiện lỗi ẩn và kiểm tra sự tương tác giữa prompt, policy và tool use.
- AI/công cụ đã dùng và cách kiểm tra: GitHub Copilot, VS Code, data JSON và quy trình chạy benchmark để kiểm tra từng case. Tôi dùng method so sánh output giữa các lần chạy và xác nhận lỗi/fix bằng transcript và run results.
- Thời điểm đã tự nộp URL repo chung trên VLearn: 16/09/2026

### Vũ Tiến Linh — 2A202602657

- Phần việc và file/commit/PR: Hoàn thiện báo cáo, cập nhật TEAM.md, kiểm tra chất lượng submission, đồng thời tham gia phần sửa prompt/tool và chạy v1–v3, version log. File chính: REPORT.md, TEAM.md, system_prompt.md, tools.yaml và các file run JSON liên quan.
- Quyết định, khó khăn và cách xử lý: Tôi tập trung vào việc tổng hợp bằng chứng từ quá trình chạy, xác định phần đã cải thiện và phần còn hạn chế, rồi chuẩn bị tài liệu báo cáo và checklist nộp. Khó khăn là đảm bảo báo cáo và TEAM.md phản ánh đúng quá trình thực tế, nên tôi đã đối chiếu lại với các file run, version log và thân chứng từ transcript.
- Điều đã học: Tôi học cách nhìn nhận dự án từ góc độ tổng quan: không chỉ là code, mà còn là bằng chứng, quy trình, và cách trình bày kết quả một cách thuyết phục. Việc kiểm tra submission và review log giúp nâng cao tính chính xác và độ tin cậy của bài nộp.
- AI/công cụ đã dùng và cách kiểm tra: GitHub Copilot, VS Code, file README và REPORT.md, plus các log/run để đối chiếu. Tôi kiểm tra bằng cách đọc lại toàn bộ nội dung và so khớp với tiến độ thực tế của nhóm trước khi nộp.
- Thời điểm đã tự nộp URL repo chung trên VLearn: 16/09/2026
