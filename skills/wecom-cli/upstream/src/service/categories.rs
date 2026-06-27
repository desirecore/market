#[derive(Debug, Clone)]
pub struct CategoryInfo {
    pub name: &'static str,
    pub description: &'static str,
    pub permission_name: &'static str,
}

/// Return all supported business categories and their tool definitions.
pub fn get_categories() -> Vec<CategoryInfo> {
    // Categories in alphabetical order
    vec![
        CategoryInfo {
            name: "contact",
            description: "通讯录 — 成员查询和搜索",
            permission_name: "通讯录",
        },
        CategoryInfo {
            name: "doc",
            description: "文档 — 文档/智能表格创建和管理",
            permission_name: "文档",
        },
        CategoryInfo {
            name: "meeting",
            description: "会议 — 创建/管理/查询视频会议",
            permission_name: "会议",
        },
        CategoryInfo {
            name: "msg",
            description: "消息 — 聊天列表、发送/接收消息、媒体下载",
            permission_name: "消息",
        },
        CategoryInfo {
            name: "schedule",
            description: "日程 — 日程增删改查和可用性查询",
            permission_name: "日程",
        },
        CategoryInfo {
            name: "todo",
            description: "待办事项 — 创建/查询/编辑待办项",
            permission_name: "待办",
        },
    ]
}
