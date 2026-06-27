export default {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // type 必须是以下之一
    'type-enum': [
      2,
      'always',
      [
        'feat', // 新功能
        'fix', // 修复 bug
        'docs', // 文档变更
        'style', // 代码格式（不影响功能）
        'refactor', // 重构（不是新功能也不是修复）
        'perf', // 性能优化
        'test', // 测试
        'build', // 构建系统或外部依赖
        'ci', // CI 配置
        'chore', // 其他杂项
        'revert', // 回滚
        'skills', // skills 更新
      ],
    ],
    // type 不能为空
    'type-empty': [2, 'never'],
    // subject 不能为空
    'subject-empty': [2, 'never'],
    // subject 最大长度
    'subject-max-length': [2, 'always', 100],
    // header 最大长度
    'header-max-length': [2, 'always', 120],
  },
};
