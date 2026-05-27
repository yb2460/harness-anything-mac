"""跨平台 Office 后端——Windows 用 WPS COM，macOS/Linux 用 LibreOffice。"""
import os, sys, platform, subprocess, tempfile, shutil

IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"

def get_backend():
    """检测平台，返回可用后端名称。"""
    if IS_WINDOWS:
        try:
            import win32com.client
            return "wps-com"
        except ImportError:
            pass
    if shutil.which("soffice") or shutil.which("libreoffice"):
        return "libreoffice-headless"
    raise RuntimeError("无可用 Office 后端。Windows 请安装 WPS Office + pywin32；Mac 请 brew install libreoffice")


def find_libreoffice():
    for name in ("soffice", "libreoffice"):
        p = shutil.which(name)
        if p: return p
    mac_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    if os.path.isfile(mac_path): return mac_path
    raise RuntimeError("LibreOffice 未安装。Mac: brew install --cask libreoffice")


def convert_to(input_path, output_format, output_path=None, overwrite=False, timeout=120):
    """用 LibreOffice headless 转换文件格式。

    Args:
        input_path: 输入文件路径（ODF/HTML等）
        output_format: 目标格式（pdf, docx, xlsx, pptx, txt, html, csv等）
        output_path: 输出文件路径。为 None 时放在输入文件同目录。

    Returns:
        {"output": 绝对路径, "format": 格式, "file_size": 字节数}
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入文件不存在: {input_path}")

    lo = find_libreoffice()
    input_path = os.path.abspath(input_path)

    output_dir = os.path.dirname(output_path) if output_path else os.path.dirname(input_path)
    os.makedirs(output_dir, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="lo-") as tmp_dir:
        cmd = [lo, "--headless", "--nologo", "--nofirststartwizard",
               "--convert-to", output_format, "--outdir", tmp_dir, input_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        if result.returncode != 0:
            raise RuntimeError(f"LibreOffice 转换失败:\n{result.stderr.strip()}")

        base = os.path.splitext(os.path.basename(input_path))[0]
        converted = os.path.join(tmp_dir, f"{base}.{output_format}")
        if not os.path.exists(converted):
            raise RuntimeError(f"未生成输出文件。期望: {converted}")

        final = output_path or os.path.join(os.path.dirname(input_path), f"{base}.{output_format}")
        if os.path.exists(final) and not overwrite:
            raise FileExistsError(f"输出文件已存在: {final}。使用 --overwrite。")
        shutil.move(converted, final)
        return {"output": os.path.abspath(final), "format": output_format,
                "file_size": os.path.getsize(final), "method": "libreoffice-headless"}


# WPS COM 后端——仅 Windows
if IS_WINDOWS:
    PROGID_MAP = {"writer": "KWPS.Application", "calc": "KET.Application", "impress": "KWPP.Application"}

    def find_wps(app_type="writer"):
        import win32com.client, pythoncom
        pythoncom.CoInitialize()
        return win32com.client.Dispatch(PROGID_MAP[app_type])

    def export_wps(doc, path, fmt, doc_type):
        fmt_map = {
            "writer": {"docx": 16, "pdf": 17, "txt": 2, "html": 10, "rtf": 6},
            "calc": {"xlsx": 51, "pdf": 0, "csv": 62, "html": 44},
            "impress": {"pptx": 1, "pdf": 32},
        }
        code = fmt_map.get(doc_type, {}).get(fmt)
        if code is None:
            doc.SaveAs2(path)
        else:
            doc.SaveAs2(path, FileFormat=code)
        return path
