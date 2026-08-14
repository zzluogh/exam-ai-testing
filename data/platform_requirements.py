"""客户端/APP/H5 端需求清单 — 各端特有测试场景。

Web 端的业务逻辑（business.py）已被接口级测试覆盖。
这三端不重复测业务逻辑，而是补充"终端形态带来的特有风险"：
  - 客户端：离线答题、本地暂存、断网重传、升级卸载
  - APP：弱网、中断打断、设备矩阵、权限、推送
  - H5：宿主环境、双端兼容、支付回调、缓存
每条需求带 来源 标注（需求明确/测试假设/标准引用/边界值）。
"""
PLATFORM_REQUIREMENTS = {
    "client": [
        {"id": "C01", "platform": "客户端", "priority": "P0",
         "requirement": "考生断网后仍可继续答题，答案保存到本地暂存文件",
         "source": "需求明确"},
        {"id": "C02", "platform": "客户端", "priority": "P0",
         "requirement": "网络恢复后，本地暂存答案自动上传服务器，且不重复提交",
         "source": "需求明确"},
        {"id": "C03", "platform": "客户端", "priority": "P1",
         "requirement": "升级客户端时保留本地未上传的暂存数据，升级后仍可继续上传",
         "source": "测试假设"},
        {"id": "C04", "platform": "客户端", "priority": "P1",
         "requirement": "卸载客户端时提示用户未上传的暂存数据，防止数据丢失",
         "source": "测试假设"},
        {"id": "C05", "platform": "客户端", "priority": "P2",
         "requirement": "客户端在低磁盘空间（<100MB）时应提示，但考试仍可继续",
         "source": "边界值"},
        {"id": "C06", "platform": "客户端", "priority": "P2",
         "requirement": "进程被强制结束后重启，未交卷的会话状态应保持可恢复",
         "source": "状态机边界"},
    ],
    "app": [
        {"id": "A01", "platform": "APP", "priority": "P0",
         "requirement": "答题过程中切换飞行模式，答案不丢失，恢复网络后自动重试提交",
         "source": "需求明确"},
        {"id": "A02", "platform": "APP", "priority": "P0",
         "requirement": "答题时来电/来短信打断，考试会话不应中断，恢复后继续",
         "source": "需求明确"},
        {"id": "A03", "platform": "APP", "priority": "P1",
         "requirement": "切到后台再回到前台，考试剩余时间正确，且不会误判为超时",
         "source": "测试假设"},
        {"id": "A04", "platform": "APP", "priority": "P1",
         "requirement": "未授权定位/相机权限时，功能正常降级而不是崩溃",
         "source": "需求明确"},
        {"id": "A05", "platform": "APP", "priority": "P2",
         "requirement": "考试期间收到系统推送通知，不应覆盖或干扰答题界面",
         "source": "测试假设"},
        {"id": "A06", "platform": "APP", "priority": "P2",
         "requirement": "同一账号在 Android/iOS 两端同时登录，应互斥踢出或提示",
         "source": "标准引用（会话管理规范）"},
    ],
    "h5": [
        {"id": "H01", "platform": "H5", "priority": "P0",
         "requirement": "H5 页面在微信/支付宝/自家 APP 三种宿主中功能一致",
         "source": "需求明确"},
        {"id": "H02", "platform": "H5", "priority": "P0",
         "requirement": "H5 内点击缴费，调起宿主支付，支付成功回传后页面状态正确更新",
         "source": "需求明确"},
        {"id": "H03", "platform": "H5", "priority": "P1",
         "requirement": "微信内打开 H5 时，分享/扫码/定位等 JS-SDK 调用需正常授权",
         "source": "需求明确"},
        {"id": "H04", "platform": "H5", "priority": "P1",
         "requirement": "H5 页面下拉刷新或返回键不丢失已填写的答题内容",
         "source": "测试假设"},
        {"id": "H05", "platform": "H5", "priority": "P2",
         "requirement": "H5 在 iOS 低版本 Safari 与 Android 老内核下渲染一致，不出现布局错乱",
         "source": "标准引用（兼容性矩阵）"},
        {"id": "H06", "platform": "H5", "priority": "P2",
         "requirement": "H5 页面被 iOS 键盘顶起/回收后，输入框位置与已填内容不偏移",
         "source": "测试假设"},
    ],
}
