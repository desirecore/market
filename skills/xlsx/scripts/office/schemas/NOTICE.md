# Office 离线 Schema 依赖

此目录包含 Office 元数据校验所需的 Dublin Core XML Schema。XML schemas Copyright © 2011 [DCMI](https://www.dublincore.org/)，按 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 使用；许可依据见 [DCMI Schema Use Notice](https://www.dublincore.org/about/copyright/)。上游 Schema 标注创建日期为 2003-04-02，原作者与文档注释保留在文件内。

|本地文件|原始来源|原始文件 SHA-256|
|---|---|---|
|`dublin-core/dc.xsd`|https://www.dublincore.org/schemas/xmls/qdc/2003/04/02/dc.xsd|`bc1d454db1bb20dfb1867a3fe0cf007775fc4afa33a5df425c12d854f049f1f6`|
|`dublin-core/dcterms.xsd`|https://www.dublincore.org/schemas/xmls/qdc/2003/04/02/dcterms.xsd|`6328c8b574c166f8ebc28d07231e6ee47121e9791689b70c3afa665f22099fed`|
|`dublin-core/dcmitype.xsd`|https://www.dublincore.org/schemas/xmls/qdc/2003/04/02/dcmitype.xsd|`4980845d0bedcf45e707fa64eb47492ae4f95ac4ae42f5c3c68b58c0bc9e8e49`|

本地适配规范化三份文件的行尾空白与缩进，并修改 `dc.xsd` / `dcterms.xsd` 的 XML 命名空间 import 路径，复用已随包提供的 `ISO-IEC29500-4_2016/xml.xsd`；`dcmitype.xsd` 仅调整空白。Office `opc-coreProperties.xsd` 改为引用本地 `dublin-core/`，不改变命名空间 URI 或类型定义。三套技能分别携带完整闭包，独立安装时不依赖其它技能目录。

离线编译与中文 XML 回归：从市场仓库根运行 `uv run scripts/office/test_offline_resources.py`。运行时仍需要 `lxml` / `defusedxml`；本文件不表示捆绑 LibreOffice 或其它办公系统工具。
