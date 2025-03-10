import PyPDF2
import os
import re
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_pdf(input_path, output_path):
    try:
        # 打开PDF文件
        with open(input_path, 'rb') as input_file:
            # 读取PDF内容
            pdf_content = input_file.read()
            
            # 使用正则表达式查找所有/MediaBox定义
            mediabox_pattern = re.compile(b'/MediaBox\s*\[.*?\]')
            matches = mediabox_pattern.finditer(pdf_content)
            
            # 记录已处理的位置
            processed_positions = set()
            
            # 创建一个新的PDF内容
            new_content = bytearray(pdf_content)
            
            # 遍历所有匹配项
            for match in matches:
                start_pos = match.start()
                
                # 检查是否已处理过该位置附近的/MediaBox
                if any(abs(start_pos - pos) < 10 for pos in processed_positions):
                    # 如果是重复的/MediaBox，则替换为空格
                    for i in range(start_pos, match.end()):
                        new_content[i] = ord(' ')
                    logger.info(f"已移除重复的/MediaBox定义，位置: {hex(start_pos)}")
                else:
                    # 记录已处理的位置
                    processed_positions.add(start_pos)
            
            # 写入修复后的PDF文件
            with open(output_path, 'wb') as output_file:
                output_file.write(new_content)
            
            # 验证修复后的PDF
            try:
                PyPDF2.PdfReader(output_path)
                logger.info(f"PDF验证成功: {output_path}")
                return True
            except Exception as e:
                logger.error(f"PDF验证失败: {str(e)}")
                return False
                
    except Exception as e:
        logger.error(f"修复PDF时出错: {str(e)}")
        return False

def fix_multiple_pdfs(input_paths, output_dir):
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 记录成功和失败的文件
    success_count = 0
    failed_files = []
    
    for input_path in input_paths:
        # 获取文件名并创建输出路径
        file_name = os.path.basename(input_path)
        output_path = os.path.join(output_dir, f"fixed_{file_name}")
        
        logger.info(f"正在修复: {input_path}")
        
        # 修复PDF
        if fix_pdf(input_path, output_path):
            success_count += 1
        else:
            failed_files.append(input_path)
    
    # 输出统计信息
    logger.info(f"修复完成。成功: {success_count}, 失败: {len(failed_files)}")
    if failed_files:
        logger.info("失败的文件:")
        for file in failed_files:
            logger.info(f"  - {file}")

# 使用示例
if __name__ == "__main__":
    import glob
    
    # 获取所有PDF文件 - 搜索多个可能的位置
    pdf_files = []
    search_paths = [
        "*.pdf",                                # 当前目录
        "../*.pdf",                             # 上级目录
        "C:/Users/13027/Desktop/*.pdf",         # 桌面
        "C:/Users/13027/Desktop/2025作战问题学习/*.pdf",         # 桌面
        os.path.join(os.path.expanduser("~"), "Desktop", "*.pdf")  # 用户桌面
    ]
    
    for path in search_paths:
        found_files = glob.glob(path)
        if found_files:
            pdf_files.extend(found_files)
            logger.info(f"在 {path} 中找到 {len(found_files)} 个PDF文件")
    
    if not pdf_files:
        logger.warning("未找到PDF文件")
        logger.info("请将PDF文件放在以下位置之一:")
        for path in search_paths:
            logger.info(f"  - {path}")
    else:
        logger.info(f"总共找到 {len(pdf_files)} 个PDF文件")
        output_directory = 'fixed_pdfs'
        fix_multiple_pdfs(pdf_files, output_directory)
