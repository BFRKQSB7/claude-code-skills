# GPU / 推理部署

> 加载条件: 任务涉及 GPU, 显卡, CUDA, Blackwell, RTX 50, DirectML, DML, onnxruntime, paddle, 推理, 模型部署, OCR

---

## ★★★ [2026-08-10] Blackwell(RTX50) 上 paddle cu126 CUDA 乱码 → 走 onnxruntime+DirectML (置信度: high, 命中: 1)

**Rule**: NVIDIA RTX 50 系 (sm_120) 上 paddle cu126 的 CUDA 推理不可用（输出乱码+比 CPU 慢），换 cuDNN/CUDA 版本修不好（paddle 自己 12.6 时代内核的锅）。GPU 推理改用 **onnxruntime + DirectML**，或先查 paddle 有无 cu128 构建（Windows 无）。
**Wrong**: 想靠升 nvidia-cudnn-cu12→9.9、cublas/cusolver/cudart→12.9 修 paddle Blackwell → 实测仍乱码（速度还正常了，说明是 paddle 内核本身）。
**Right**: onnxruntime-directml（D3D12 抽象，与厂商无关）→ Blackwell 正常，0.09s vs paddle CPU 5.8s。LunaTranslator 同机制（det.onnx/rec.onnx + ORT + DML EP），源码+文档印证。
**Why**: paddle cu126 是 CUDA 12.6 时代构建，sm_120 内核残缺；DML 走硬件抽象层绕开。Windows 上 paddle 3.x GPU 只有 cu126（cu128 无 win 轮子）。

---

## ★ [2026-08-10] GPU 硬件探测不能依赖加速包本身（删模块后无法重装）(命中: 1)

**Rule**: 探测「硬件是否支持 GPU 加速」必须独立于加速库（onnxruntime-directml 提供 DML provider，删了就没法检测 → 重装被拒 = 鸡生蛋）。用系统 API 单独探测硬件。
**Wrong**: 用 `onnxruntime.get_available_providers()` 含 DmlExecutionProvider 判硬件 → 模块删除后返回空 → 重装被拒。
**Right**: ctypes `D3D11CreateDevice(NULL, DRIVER_HARDWARE)` 判硬件；模块是否安装用 `importlib.metadata` 单独查；「符合要求」= 硬件 && 模块。
**Why**: 硬件能力与加速库安装是两回事；删除必须可逆（换设备后能重装）。config 加 `gpu_explicit` 区分「用户显式关」与「默认未设」防自动覆盖。

---

## ★ [2026-08-10] ctypes 探测 D3D12CreateDevice 返回 E_NOINTERFACE → 用 D3D11CreateDevice (命中: 1)

**Rule**: 想用 ctypes 探测显卡/DX 能力，D3D12CreateDevice 可能返回 E_NOINTERFACE（即便 GUID 字节用 uuid.bytes_le 验证过）——改用无 vtable 的 D3D11CreateDevice(HARDWARE) 更可靠。
**Wrong**: `D3D12CreateDevice(NULL, FL11, &ID3D12Device, &dev)` → hr=0x80004002，argtypes/原始 GUID 缓冲/ppDevice=None 都试过无效。
**Right**: `d3d11.D3D11CreateDevice(None, 1, 0, 0, &FL11_0, 1, 7, &dev, None, &ctx) == 0` → 硬件 D3D11 设备可创建即符合要求。
**Why**: 探测目标=「能否创建硬件设备」非「能否拿 D3D12 接口」；D3D11 调用无 COM vtable 手工调用坑。

---

## 泛化 [2026-08-10] onnxruntime-directml 与 onnxruntime 同名互斥 (命中: 1)

**泛化**: onnxruntime-directml 提供同名 `onnxruntime` 模块且互斥安装（装 DML 覆盖 CPU，卸载装回 CPU）→ 天然实现「GPU 加速模块可删/可重装」，无需自己维护两套运行时。
**核心**: 依赖设计把「可选加速」做成一键安装/卸载的包切换，而非编译期开关。
