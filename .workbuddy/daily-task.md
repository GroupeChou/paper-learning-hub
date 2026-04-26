请在 WorkBuddy 中使用 `paper-learning-hub` 技能完成这个项目的每日自动研学任务。

项目目录：`/Users/zhouqunchen/Desktop/study/paper-learning-hub`

固定流程：
1. 运行 `./run_daily.sh --prepare-workbuddy`
2. 打开 `.workbuddy/daily-brief.md`
3. 逐篇处理 `.workbuddy/jobs/<paper_id>/job.md`
4. 将精读结果写入 `papers/zh/<paper_id>/paper_zh.md`
5. 写入对应 `result.json`
6. 运行 `./run_daily.sh --build-only`
7. 确认 Git 自动提交和推送状态
